"""Simulated device-check tools for skills-agent.

These return canned, deterministic data for a small fixed set of devices —
there is no real network I/O here. That's deliberate: it keeps this example
runnable end-to-end (`ncp validate`, `ncp playground`) without a lab network
or a configured connector, the same way calculator-agent/hello-agent stay
fully local. In a real agent, replace these with real SSH/SNMP/API calls
(see cisco-switch-agent for a real-device example), or with
`Agent(connectors=[...])` against a live NetBox/SNMP/Splunk source instead
of hand-written tools.
"""

from ncp import tool

_DEVICES = {
    "core-sw-01": {
        "reachable": True,
        "vendor": "Cisco",
        "model": "Catalyst 9300",
        "uptime_days": 214,
    },
    "edge-sw-07": {
        "reachable": False,
        "vendor": "Cisco",
        "model": "Catalyst 9200L",
        "uptime_days": 0,
    },
    "access-sw-12": {
        "reachable": True,
        "vendor": "Arista",
        "model": "7050X3",
        "uptime_days": 42,
    },
}

_INTERFACE_ISSUES = {
    ("access-sw-12", "Gi1/0/3"): {
        "status": "up",
        "errors": {"crc_errors": 1842, "input_drops": 37},
    },
}

# hostname, interface -> utilization percent. Deliberately independent of
# _INTERFACE_ISSUES above: access-sw-12's Gi1/0/3 has real errors but low
# utilization (an error problem, not a capacity problem), while core-sw-01's
# uplink has high utilization and no errors (a genuine capacity problem) —
# so capacity-check's "rule out errors first" step actually has something to
# rule out.
_UTILIZATION = {
    ("core-sw-01", "Te1/1/1"): 92.4,
    ("access-sw-12", "Gi1/0/3"): 21.8,
}


@tool
def get_device_inventory(hostname: str) -> dict:
    """Look up basic inventory info (vendor, model, uptime) for a device by
    hostname. Use this first to confirm the device exists before checking
    reachability or interfaces."""
    device = _DEVICES.get(hostname)
    if device is None:
        return {"found": False, "error": f"No device named '{hostname}' in inventory"}
    return {
        "found": True,
        "hostname": hostname,
        "vendor": device["vendor"],
        "model": device["model"],
        "uptime_days": device["uptime_days"],
    }


@tool
def ping_device(hostname: str) -> dict:
    """Check whether a device is reachable (simulated ICMP ping). Returns
    reachable=True/False and, when reachable, a simulated round-trip time."""
    device = _DEVICES.get(hostname)
    if device is None:
        return {"reachable": False, "error": f"No device named '{hostname}' in inventory"}
    if not device["reachable"]:
        return {"reachable": False, "hostname": hostname}
    return {"reachable": True, "hostname": hostname, "rtt_ms": 1.2}


@tool
def check_interface_status(hostname: str, interface: str) -> dict:
    """Check the operational status and error counters of one interface on a
    device (e.g. hostname='access-sw-12', interface='Gi1/0/3'). Only call
    this after confirming the device itself is reachable — checking an
    interface on an unreachable device just returns a lookup failure."""
    device = _DEVICES.get(hostname)
    if device is None:
        return {"error": f"No device named '{hostname}' in inventory"}
    if not device["reachable"]:
        return {"error": f"'{hostname}' is unreachable; interface status unavailable"}

    issue = _INTERFACE_ISSUES.get((hostname, interface))
    if issue is not None:
        return {"hostname": hostname, "interface": interface, **issue}
    return {"hostname": hostname, "interface": interface, "status": "up", "errors": {}}


@tool
def get_interface_utilization(hostname: str, interface: str) -> dict:
    """Get the current bandwidth utilization percentage for one interface on
    a device. Only meaningful on a reachable device — check ping_device
    first."""
    device = _DEVICES.get(hostname)
    if device is None:
        return {"error": f"No device named '{hostname}' in inventory"}
    if not device["reachable"]:
        return {"error": f"'{hostname}' is unreachable; utilization unavailable"}

    utilization = _UTILIZATION.get((hostname, interface), 35.0)
    return {
        "hostname": hostname,
        "interface": interface,
        "utilization_percent": utilization,
    }
