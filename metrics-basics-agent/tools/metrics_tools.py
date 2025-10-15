from typing import List, Dict, Any, Optional
from ncp import tool

from ncp.metrics import Metrics


@tool
def get_device_inventory(
    layer: Optional[str] = None, region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query the network device inventory with optional filtering.

    This tool retrieves all devices from the network inventory. You can filter
    by device layer (spine, leaf, border) or region to narrow results.

    Args:
        layer: Optional device layer filter (e.g., "spine", "leaf", "border")
        region: Optional region filter (e.g., "datacenter-1", "us-west")

    Returns:
        Dictionary containing:
        - devices: List of device objects with hostname, layer, region, model, status
        - total_count: Number of devices found
        - filters_applied: Dict showing which filters were used

    Example:
        >>> get_device_inventory(layer="spine")
        {
            "devices": [
                {"hostname": "spine-01", "layer": "spine", "region": "dc1", ...},
                {"hostname": "spine-02", "layer": "spine", "region": "dc1", ...}
            ],
            "total_count": 2,
            "filters_applied": {"layer": "spine"}
        }
    """
    # Initialize Metrics client
    metrics = Metrics()

    try:
        # Build query filters
        filters = {}
        if layer:
            filters["layer"] = layer
        if region:
            filters["region"] = region

        # Query devices from Metrics API
        devices = metrics.get_devices(**filters)

        return {
            "devices": devices,
            "total_count": len(devices),
            "filters_applied": filters
            or {"note": "No filters applied - showing all devices"},
        }
    finally:
        # Always close the Metrics client
        metrics.close()


@tool
def check_device_status(hostname: str) -> Dict[str, Any]:
    """
    Check the operational status of a specific network device.

    This tool queries the device status including reachability, uptime, and
    basic health indicators.

    Args:
        hostname: Device hostname to check (e.g., "spine-01")

    Returns:
        Dictionary containing:
        - hostname: Device hostname
        - reachable: Boolean indicating if device is reachable
        - status: Status string ("up", "down", "unreachable")
        - last_seen: Timestamp of last successful contact
        - uptime_seconds: Device uptime in seconds
        - management_ip: Management IP address
        - additional_info: Dict with extra status details

    Example:
        >>> check_device_status("spine-01")
        {
            "hostname": "spine-01",
            "reachable": True,
            "status": "up",
            "last_seen": "2024-01-16 10:30:45",
            "uptime_seconds": 3888000,
            ...
        }
    """
    # Initialize Metrics client
    metrics = Metrics()

    try:
        # Query device status from Metrics API
        device_status = metrics.get_device_status(hostname=hostname)

        if device_status:
            return device_status
        else:
            return {
                "hostname": hostname,
                "reachable": False,
                "status": "not_found",
                "error": f"Device '{hostname}' not found in inventory",
                "suggestion": "Check hostname spelling or use get_device_inventory() to see all devices",
            }
    finally:
        # Always close the Metrics client
        metrics.close()


@tool
def list_interfaces(hostname: str, status: Optional[str] = None) -> Dict[str, Any]:
    """
    List all network interfaces on a device with optional status filtering.

    This tool retrieves interface information including names, status, speed,
    and configuration details.

    Args:
        hostname: Device hostname (e.g., "spine-01")
        status: Optional filter by interface status ("up", "down", "admin-down")

    Returns:
        Dictionary containing:
        - hostname: Device hostname
        - interfaces: List of interface objects
        - total_count: Total number of interfaces
        - up_count: Number of interfaces in "up" state
        - down_count: Number of interfaces in "down" state

    Example:
        >>> list_interfaces("spine-01", status="up")
        {
            "hostname": "spine-01",
            "interfaces": [
                {"name": "Ethernet1", "status": "up", "speed": "100G", ...},
                {"name": "Ethernet2", "status": "up", "speed": "100G", ...}
            ],
            "total_count": 2,
            "up_count": 2,
            "down_count": 0
        }
    """
    # Initialize Metrics client
    metrics = Metrics()

    try:
        # Query interfaces from Metrics API
        all_interfaces = metrics.get_interfaces(hostname=hostname)

        if all_interfaces is None:
            return {
                "hostname": hostname,
                "error": f"Device '{hostname}' not found or has no interface data",
                "interfaces": [],
                "total_count": 0,
            }

        # Filter by status if specified
        if status:
            interfaces = [
                iface for iface in all_interfaces if iface.get("status") == status
            ]
        else:
            interfaces = all_interfaces

        # Count interface states
        up_count = len([i for i in all_interfaces if i.get("status") == "up"])
        down_count = len([i for i in all_interfaces if i.get("status") == "down"])

        return {
            "hostname": hostname,
            "interfaces": interfaces,
            "total_count": len(interfaces),
            "filter_applied": status or "none",
            "summary": {
                "total_interfaces": len(all_interfaces),
                "up": up_count,
                "down": down_count,
            },
        }
    finally:
        # Always close the Metrics client
        metrics.close()


@tool
def get_device_details(hostname: str) -> Dict[str, Any]:
    """
    Get comprehensive details about a network device.

    This tool provides complete device information including hardware specs,
    software versions, status, interfaces summary, and operational metrics.

    Args:
        hostname: Device hostname (e.g., "spine-01")

    Returns:
        Dictionary containing:
        - basic_info: Hostname, model, layer, region
        - hardware: Hardware specifications
        - software: OS version, software details
        - status: Operational status and uptime
        - interfaces_summary: Count and status summary
        - performance: CPU, memory, temperature metrics

    Example:
        >>> get_device_details("spine-01")
        {
            "basic_info": {"hostname": "spine-01", "model": "Arista-7050", ...},
            "hardware": {"serial": "ABC123", "chassis": "7050SX-128", ...},
            ...
        }
    """
    # Initialize Metrics client
    metrics = Metrics()

    try:
        # Get comprehensive device details from Metrics API
        details = metrics.get_device_details(hostname=hostname)

        if details:
            return details
        else:
            return {
                "error": f"Device '{hostname}' not found in inventory",
                "hostname": hostname,
                "suggestion": "Use get_device_inventory() to see all available devices",
            }
    finally:
        # Always close the Metrics client
        metrics.close()
