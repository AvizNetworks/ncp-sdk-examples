"""Cisco switch tools for cisco-switch-agent.

These tools SSH into Cisco switches (IOS / IOS-XE / NX-OS / IOS-XR) using
Netmiko and run read-only ``show`` commands to collect inventory, health,
and traffic data.

Credentials are read from a devices file (``devices.yaml`` by default) whose
entries carry ``mgmtIP``, ``username``, and ``password`` for each switch. The
agent never has to prompt the user for credentials — it looks the switch up
in this file by name or management IP.
"""

import os
from typing import Optional

from ncp import tool

try:
    from netmiko import ConnectHandler
    _NETMIKO_AVAILABLE = True
except ImportError:
    _NETMIKO_AVAILABLE = False

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ---------------------------------------------------------------------------
# Devices file handling
# ---------------------------------------------------------------------------

def _devices_file_path() -> str:
    """Resolve the path to the devices file.

    Honors the ``CISCO_DEVICES_FILE`` environment variable, otherwise falls
    back to ``devices.yaml`` sitting next to the agent package.
    """
    override = os.environ.get("CISCO_DEVICES_FILE")
    if override:
        return override
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "devices.yaml")


def _load_devices() -> tuple[list[dict], Optional[str]]:
    """Load and normalize the device inventory from the devices file.

    Returns a ``(devices, error)`` tuple. ``error`` is ``None`` on success.
    """
    if not _YAML_AVAILABLE:
        return [], "PyYAML is not installed. Add 'pyyaml' to requirements.txt."

    path = _devices_file_path()
    if not os.path.exists(path):
        return [], f"Devices file not found: {path}. Set CISCO_DEVICES_FILE or create devices.yaml."

    try:
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:
        return [], f"Failed to parse devices file {path}: {exc}"

    raw = data.get("devices", data) if isinstance(data, dict) else data
    if not isinstance(raw, list):
        return [], f"Devices file {path} must contain a 'devices:' list."

    devices: list[dict] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        mgmt_ip = entry.get("mgmtIP") or entry.get("mgmt_ip") or entry.get("host")
        if not mgmt_ip:
            continue
        devices.append({
            "name": entry.get("name") or mgmt_ip,
            "mgmtIP": str(mgmt_ip),
            "username": entry.get("username"),
            "password": entry.get("password"),
            "device_type": entry.get("device_type", "cisco_ios"),
            "secret": entry.get("secret", ""),
            "port": int(entry.get("port", 22)),
        })
    return devices, None


def _find_device(devices: list[dict], target: str) -> Optional[dict]:
    """Match a device by name (case-insensitive) or management IP."""
    t = target.strip().lower()
    for d in devices:
        if d["mgmtIP"] == target or d["name"].lower() == t:
            return d
    return None


def _connect_params(device: dict) -> dict:
    return {
        "device_type": device["device_type"],
        "host": device["mgmtIP"],
        "username": device["username"],
        "password": device["password"],
        "secret": device.get("secret", ""),
        "port": device.get("port", 22),
        "fast_cli": False,
    }


# Show-command sets per category, keyed by broad platform family.
# NX-OS uses slightly different commands than classic IOS/IOS-XE.
_COMMANDS = {
    "inventory": {
        "default": ["show version", "show inventory"],
        "cisco_nxos": ["show version", "show inventory", "show module"],
        "cisco_xr": ["show version", "show inventory", "show platform"],
    },
    "health": {
        "default": [
            "show processes cpu | include CPU",
            "show processes memory | include Processor|Total",
            "show environment",
        ],
        "cisco_nxos": [
            "show system resources",
            "show processes cpu sort",
            "show environment",
        ],
        "cisco_xr": [
            "show processes cpu",
            "show memory summary",
            "show environment all",
        ],
    },
    "traffic": {
        "default": ["show interfaces summary", "show interfaces counters"],
        "cisco_nxos": ["show interface counters", "show interface counters errors"],
        "cisco_xr": ["show interfaces summary", "show interfaces accounting"],
    },
}


def _commands_for(category: str, device_type: str) -> list[str]:
    per_cat = _COMMANDS[category]
    return per_cat.get(device_type, per_cat["default"])


def _run_show_commands(device: dict, commands: list[str]) -> dict:
    """SSH into one device and run a list of show commands.

    Returns a dict with ``outputs`` (command -> text) or an ``error`` field.
    """
    if not _NETMIKO_AVAILABLE:
        return {"error": "netmiko is not installed. Add 'netmiko' to requirements.txt."}

    if not device.get("username") or not device.get("password"):
        return {"error": f"Device '{device['name']}' is missing username/password in the devices file."}

    outputs: dict[str, str] = {}
    try:
        with ConnectHandler(**_connect_params(device)) as conn:
            if device.get("secret"):
                try:
                    conn.enable()
                except Exception:
                    pass  # best-effort; many read-only accounts don't need enable
            for cmd in commands:
                try:
                    outputs[cmd] = conn.send_command(cmd, read_timeout=60)
                except Exception as exc:
                    outputs[cmd] = f"<command failed: {exc}>"
    except Exception as exc:
        return {"error": f"SSH to {device['name']} ({device['mgmtIP']}) failed: {exc}"}

    return {"outputs": outputs}


def _collect(target: Optional[str], category: str) -> dict:
    """Shared driver: resolve devices, run the category's commands, return results."""
    devices, err = _load_devices()
    if err:
        return {"error": err}
    if not devices:
        return {"error": "No devices defined in the devices file."}

    if target:
        dev = _find_device(devices, target)
        if not dev:
            known = ", ".join(f"{d['name']} ({d['mgmtIP']})" for d in devices)
            return {"error": f"Device '{target}' not found. Known devices: {known}"}
        selected = [dev]
    else:
        selected = devices

    results = []
    for dev in selected:
        commands = _commands_for(category, dev["device_type"])
        run = _run_show_commands(dev, commands)
        results.append({
            "name": dev["name"],
            "mgmtIP": dev["mgmtIP"],
            "device_type": dev["device_type"],
            "commands": commands,
            **run,
        })

    return {"category": category, "device_count": len(results), "results": results}


# ---------------------------------------------------------------------------
# Tools exposed to the agent
# ---------------------------------------------------------------------------

@tool
def list_devices() -> dict:
    """List the Cisco switches defined in the devices file.

    Reads the devices file (``devices.yaml`` or ``$CISCO_DEVICES_FILE``) and
    returns each switch's name, management IP, and Netmiko device type.
    Passwords are NOT returned.

    Returns:
        Dict with ``device_count`` and a ``devices`` list of
        ``{name, mgmtIP, device_type}`` entries, or an ``error`` field.
    """
    devices, err = _load_devices()
    if err:
        return {"error": err}
    return {
        "device_count": len(devices),
        "devices": [
            {"name": d["name"], "mgmtIP": d["mgmtIP"], "device_type": d["device_type"]}
            for d in devices
        ],
    }


@tool
def get_inventory(device: Optional[str] = None) -> dict:
    """Collect hardware/software inventory from Cisco switch(es).

    SSHes in and runs inventory ``show`` commands (``show version``,
    ``show inventory``, plus ``show module``/``show platform`` on NX-OS/XR)
    to report model, serial numbers, software version, and installed modules.

    Args:
        device: Switch name or management IP to target. If omitted, runs
            against ALL switches in the devices file.

    Returns:
        Dict with per-device raw command outputs, or an ``error`` field.
    """
    return _collect(device, "inventory")


@tool
def get_health(device: Optional[str] = None) -> dict:
    """Collect health/resource metrics from Cisco switch(es).

    SSHes in and runs health ``show`` commands (CPU, memory, and environment/
    power/temperature) so the agent can assess whether a switch is healthy.
    Command set adapts to the platform (IOS vs NX-OS vs IOS-XR).

    Args:
        device: Switch name or management IP to target. If omitted, runs
            against ALL switches in the devices file.

    Returns:
        Dict with per-device raw command outputs, or an ``error`` field.
    """
    return _collect(device, "health")


@tool
def get_traffic(device: Optional[str] = None) -> dict:
    """Collect interface traffic and counters from Cisco switch(es).

    SSHes in and runs traffic ``show`` commands (interface summary, byte/packet
    counters, and error counters) to report link utilization and error rates.

    Args:
        device: Switch name or management IP to target. If omitted, runs
            against ALL switches in the devices file.

    Returns:
        Dict with per-device raw command outputs, or an ``error`` field.
    """
    return _collect(device, "traffic")


@tool
def run_show_command(device: str, command: str) -> dict:
    """Run an arbitrary read-only ``show`` command on one Cisco switch.

    Use this for anything the inventory/health/traffic tools don't cover
    (e.g. ``show ip interface brief``, ``show cdp neighbors``,
    ``show mac address-table``). Only ``show`` commands are permitted — this
    tool refuses configuration or exec commands.

    Args:
        device: Switch name or management IP to target (required).
        command: The ``show`` command to execute (must start with "show").

    Returns:
        Dict with the command ``output``, or an ``error`` field.
    """
    if not command.strip().lower().startswith("show"):
        return {"error": "Only 'show' commands are allowed by this tool."}

    devices, err = _load_devices()
    if err:
        return {"error": err}
    dev = _find_device(devices, device)
    if not dev:
        known = ", ".join(f"{d['name']} ({d['mgmtIP']})" for d in devices)
        return {"error": f"Device '{device}' not found. Known devices: {known}"}

    run = _run_show_commands(dev, [command])
    if "error" in run:
        return run
    return {
        "name": dev["name"],
        "mgmtIP": dev["mgmtIP"],
        "command": command,
        "output": run["outputs"].get(command, ""),
    }
