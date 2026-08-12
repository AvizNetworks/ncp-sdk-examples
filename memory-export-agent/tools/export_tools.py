"""Tools for memory-export-agent.

Demonstrates Memory().store(..., exportable=True) and Memory().get_metadata():
data stored with exportable=True can be downloaded as a raw CSV/JSON file via
the platform's auto-injected export_data_from_memory UI tool (a "Download CSV
/ Download JSON" card) or the REST endpoint it calls under the hood -
bypassing the LLM and the chat UI's HTML entirely.
"""

import random
from typing import Any, Dict, List

from ncp import Memory, tool

_STATUSES = ["healthy", "healthy", "healthy", "degraded", "unreachable"]
_ROLES = ["core-switch", "edge-router", "access-switch", "firewall"]


def _generate_inventory(row_count: int) -> List[Dict[str, Any]]:
    rows = []
    for i in range(1, row_count + 1):
        rows.append({
            "hostname": f"device-{i:03d}",
            "role": random.choice(_ROLES),
            "status": random.choice(_STATUSES),
            "firmware": f"{random.randint(14, 17)}.{random.randint(0, 9)}",
            "uptime_days": random.randint(1, 900),
        })
    return rows


@tool
def generate_device_inventory(row_count: int = 50, exportable: bool = True) -> Dict[str, Any]:
    """Generate a synthetic device inventory report and store it in agent memory.

    Simulates what a real inventory/NetBox tool would return. Stored via
    Memory().store(..., exportable=...) - pass exportable=True (the default)
    to make the dataset downloadable as a file afterward, or exportable=False
    to see what happens when a download is attempted on a non-exportable entry.

    Args:
        row_count: Number of device rows to generate (1-500)
        exportable: Whether this entry should be user-downloadable as a file

    Returns:
        A dict with reference_id, record_count, description, and exportable
    """
    row_count = max(1, min(row_count, 500))
    rows = _generate_inventory(row_count)
    description = f"Device inventory report ({row_count} devices)"

    reference_id = Memory().store(
        data=rows,
        data_type="device_inventory",
        description=description,
        exportable=exportable,
    )

    return {
        "reference_id": reference_id,
        "record_count": len(rows),
        "description": description,
        "exportable": exportable,
    }


@tool
def get_dataset_info(reference_id: str) -> Dict[str, Any]:
    """Look up metadata for a stored dataset without loading its full payload.

    Wraps Memory().get_metadata() - a cheap discovery call that returns
    record_count, size, schema_hint, and (relevant here) whether the entry
    is exportable, so you can check before asking a user to try downloading it.

    Args:
        reference_id: The reference ID returned by generate_device_inventory

    Returns:
        The metadata dict, or an 'error' key if the reference is missing/expired
    """
    try:
        return Memory().get_metadata(reference_id)
    except KeyError:
        return {
            "error": f"No dataset found for reference_id '{reference_id}'. "
                     "It may have expired (TTL: 1 hour) or the ID is incorrect.",
            "reference_id": reference_id,
        }
