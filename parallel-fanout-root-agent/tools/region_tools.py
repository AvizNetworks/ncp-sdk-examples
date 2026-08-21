"""Per-region health lookup tools for the fan-out example."""

from ncp import tool

_REGION_HEALTH = {
    "us-east": {
        "devices_total": 214,
        "devices_down": 2,
        "interface_errors_24h": 118,
        "notes": "spine-03 rebooted overnight; err-disabled port on leaf-11",
    },
    "us-west": {
        "devices_total": 168,
        "devices_down": 0,
        "interface_errors_24h": 9,
        "notes": "no incidents in the last 24h",
    },
    "eu-central": {
        "devices_total": 97,
        "devices_down": 1,
        "interface_errors_24h": 402,
        "notes": "sustained CRC errors on the dc-fra transit link",
    },
}


@tool
def get_region_health(region: str) -> dict:
    """Get the current health snapshot for one region.

    Args:
        region: Region name, e.g. "us-east", "us-west", "eu-central"

    Returns:
        A dict with device counts, 24h interface error totals, and operator
        notes, or an 'error' key if the region is unknown.
    """
    snapshot = _REGION_HEALTH.get(region.strip().lower())
    if snapshot is None:
        return {
            "error": f"Unknown region {region!r}",
            "known_regions": sorted(_REGION_HEALTH),
        }
    return {"region": region.strip().lower(), **snapshot}


@tool
def list_regions() -> dict:
    """List every region that can be health-checked.

    Returns:
        A dict with the sorted list of known region names.
    """
    return {"regions": sorted(_REGION_HEALTH)}
