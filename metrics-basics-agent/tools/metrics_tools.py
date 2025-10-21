from typing import Dict, Any, Optional
from ncp import tool, Metrics


@tool
def get_device_inventory(
    ip_address: Optional[str] = None,
    layer: Optional[str] = None,
    region: Optional[str] = None,
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
    """
    # Initialize Metrics client
    metrics = Metrics()

    try:
        # Build query filters
        filters = {}
        if ip_address:
            filters["ip_address"] = ip_address
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
