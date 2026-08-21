"""Per-device security posture tools for the concurrent-specialists example."""

from ncp import tool

_FIRMWARE = {
    "core-sw-01": {"version": "15.2(7)E3", "eol": True, "eol_date": "2023-01-31"},
    "edge-fw-02": {"version": "9.16.4", "eol": False, "eol_date": None},
    "access-sw-03": {"version": "16.9.1", "eol": True, "eol_date": "2024-06-30"},
}

_EXPOSURE = {
    "core-sw-01": {"open_ports": [22, 23, 80], "exposed_services": ["telnet", "http-admin"]},
    "edge-fw-02": {"open_ports": [22, 443], "exposed_services": ["ssh", "https-admin"]},
    "access-sw-03": {"open_ports": [22, 80, 161], "exposed_services": ["http-admin", "snmp-v1"]},
}

_AUTH = {
    "core-sw-01": {"default_credentials": False, "auth_method": "tacacs+", "mfa": False},
    "edge-fw-02": {"default_credentials": False, "auth_method": "radius", "mfa": True},
    "access-sw-03": {"default_credentials": True, "auth_method": "local", "mfa": False},
}


@tool
def get_firmware_status(device: str) -> dict:
    """Get a device's firmware version and end-of-life status.

    Args:
        device: Device name, e.g. "core-sw-01"

    Returns:
        A dict with 'version', 'eol' (bool), and 'eol_date', or an 'error'
        key if the device is unknown.
    """
    record = _FIRMWARE.get(device.strip().lower())
    if record is None:
        return {"error": f"Unknown device {device!r}", "known_devices": sorted(_FIRMWARE)}
    return {"device": device.strip().lower(), **record}


@tool
def get_open_ports(device: str) -> dict:
    """Get a device's open ports and exposed services.

    Args:
        device: Device name, e.g. "core-sw-01"

    Returns:
        A dict with 'open_ports' and 'exposed_services', or an 'error' key
        if the device is unknown.
    """
    record = _EXPOSURE.get(device.strip().lower())
    if record is None:
        return {"error": f"Unknown device {device!r}", "known_devices": sorted(_EXPOSURE)}
    return {"device": device.strip().lower(), **record}


@tool
def get_auth_config(device: str) -> dict:
    """Get a device's authentication configuration.

    Args:
        device: Device name, e.g. "core-sw-01"

    Returns:
        A dict with 'default_credentials' (bool), 'auth_method', and 'mfa'
        (bool), or an 'error' key if the device is unknown.
    """
    record = _AUTH.get(device.strip().lower())
    if record is None:
        return {"error": f"Unknown device {device!r}", "known_devices": sorted(_AUTH)}
    return {"device": device.strip().lower(), **record}
