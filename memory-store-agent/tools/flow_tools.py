"""Network flow analysis tools for memory-store-agent.

Demonstrates the agent memory store pattern:
  - generate_flow_data: stores a large dataset in memory, returns a reference_id
  - top_talkers / protocol_breakdown: retrieve by reference_id, process server-side,
    return only a small summary — the full dataset never enters the LLM context
  - list_datasets / drop_dataset: memory lifecycle management
"""

import random
from typing import Any, Dict, List, Optional

from ncp import Memory, tool

# Synthetic data helpers

_PROTOCOLS = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH", "SNMP"]
_PRIVATE_PREFIXES = ["10.0", "10.1", "192.168.1", "192.168.10", "172.16.0"]


def _random_ip(prefix: Optional[str] = None) -> str:
    pfx = prefix or random.choice(_PRIVATE_PREFIXES)
    return f"{pfx}.{random.randint(1, 254)}"


def _generate_records(device_count: int, records_per_device: int) -> List[Dict[str, Any]]:
    """Generate synthetic flow records."""
    records = []
    devices = [f"device-{i:02d}" for i in range(1, device_count + 1)]
    for device in devices:
        src_prefix = random.choice(_PRIVATE_PREFIXES)
        for _ in range(records_per_device):
            records.append({
                "src_ip": _random_ip(src_prefix),
                "dst_ip": _random_ip(),
                "protocol": random.choice(_PROTOCOLS),
                "src_port": random.randint(1024, 65535),
                "dst_port": random.choice([80, 443, 22, 53, 8080, 3306, 5432]),
                "bytes": random.randint(64, 1_500_000),
                "packets": random.randint(1, 1000),
                "device": device,
            })
    return records


# Tools

@tool
def generate_flow_data(device_count: int = 10, records_per_device: int = 100) -> Dict[str, Any]:
    """Generate synthetic network flow records and store them in agent memory.

    Simulates what an Elasticsearch or NetFlow MCP tool would return — a large
    collection of flow records. The records are stored in memory and only a
    reference_id is returned, keeping the LLM context window free.

    Args:
        device_count: Number of network devices to generate flows for (1–50).
            Each device produces a distinct source IP prefix.
        records_per_device: Number of flow records per device (1–500).
            Total records = device_count × records_per_device.

    Returns:
        Dictionary containing:
        - reference_id (str): 8-character ID — pass this to analysis tools
        - record_count (int): total number of flow records stored
        - description (str): human-readable label for this dataset

    Examples:
        >>> generate_flow_data(device_count=5, records_per_device=200)
        {"reference_id": "a1b2c3d4", "record_count": 1000, "description": "..."}

        >>> generate_flow_data()  # defaults: 10 devices × 100 records = 1000 total
        {"reference_id": "e5f6g7h8", "record_count": 1000, "description": "..."}
    """
    device_count = max(1, min(device_count, 50))
    records_per_device = max(1, min(records_per_device, 500))

    records = _generate_records(device_count, records_per_device)
    description = (
        f"Synthetic flow data — {device_count} devices × {records_per_device} records"
    )

    reference_id = Memory().store(
        data=records,
        data_type="network_flows",
        description=description,
    )

    return {
        "reference_id": reference_id,
        "record_count": len(records),
        "description": description,
    }


@tool
def top_talkers(reference_id: str, top_n: int = 10) -> Dict[str, Any]:
    """Find the top N source IP addresses by total bytes transferred.

    Retrieves the stored flow dataset by reference_id and aggregates bytes
    per source IP entirely in Python — the full dataset never enters the LLM
    context window. Only the final top-N summary is returned.

    Args:
        reference_id: The 8-character ID returned by generate_flow_data (or
            any other tool that stored flow records in memory).
        top_n: Number of top source IPs to return (default: 10, max: 50).

    Returns:
        Dictionary containing:
        - top_talkers (list): ranked list of dicts with src_ip, total_bytes,
          total_packets, flow_count
        - total_records_analysed (int): how many flow records were processed
        - reference_id (str): echoed back for traceability

    Examples:
        >>> top_talkers(reference_id="a1b2c3d4", top_n=5)
        {
          "top_talkers": [
            {"rank": 1, "src_ip": "10.0.1.42", "total_bytes": 4823100, ...},
            ...
          ],
          "total_records_analysed": 1000,
          "reference_id": "a1b2c3d4"
        }
    """
    top_n = max(1, min(top_n, 50))

    try:
        records = Memory().retrieve(reference_id)
    except KeyError:
        return {
            "error": f"No dataset found for reference_id '{reference_id}'. "
                     "It may have expired (TTL: 1 hour) or the ID is incorrect.",
            "reference_id": reference_id,
        }

    # Aggregate bytes and packets per source IP
    aggregated: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        src = rec.get("src_ip", "unknown")
        if src not in aggregated:
            aggregated[src] = {"total_bytes": 0, "total_packets": 0, "flow_count": 0}
        aggregated[src]["total_bytes"] += rec.get("bytes", 0)
        aggregated[src]["total_packets"] += rec.get("packets", 0)
        aggregated[src]["flow_count"] += 1

    ranked = sorted(aggregated.items(), key=lambda x: x[1]["total_bytes"], reverse=True)

    result = []
    for rank, (src_ip, stats) in enumerate(ranked[:top_n], start=1):
        result.append({
            "rank": rank,
            "src_ip": src_ip,
            "total_bytes": stats["total_bytes"],
            "total_packets": stats["total_packets"],
            "flow_count": stats["flow_count"],
        })

    return {
        "top_talkers": result,
        "total_records_analysed": len(records),
        "reference_id": reference_id,
    }


@tool
def protocol_breakdown(reference_id: str) -> Dict[str, Any]:
    """Group flow records by protocol and sum bytes per protocol.

    Retrieves the stored flow dataset and computes a protocol-level traffic
    breakdown — useful for understanding traffic composition. Processing is
    done server-side; only the aggregated result is returned to the LLM.

    Args:
        reference_id: The 8-character ID returned by generate_flow_data (or
            any other tool that stored flow records in memory).

    Returns:
        Dictionary containing:
        - breakdown (list): list of dicts with protocol, total_bytes,
          total_packets, flow_count, pct_bytes — sorted by total_bytes desc
        - total_bytes (int): grand total bytes across all protocols
        - total_records_analysed (int): number of flow records processed
        - reference_id (str): echoed back for traceability

    Examples:
        >>> protocol_breakdown(reference_id="a1b2c3d4")
        {
          "breakdown": [
            {"protocol": "TCP", "total_bytes": 3200000, "pct_bytes": 66.2, ...},
            {"protocol": "UDP", "total_bytes": 1100000, "pct_bytes": 22.8, ...},
            ...
          ],
          "total_bytes": 4834000,
          "total_records_analysed": 1000,
          "reference_id": "a1b2c3d4"
        }
    """
    try:
        records = Memory().retrieve(reference_id)
    except KeyError:
        return {
            "error": f"No dataset found for reference_id '{reference_id}'. "
                     "It may have expired (TTL: 1 hour) or the ID is incorrect.",
            "reference_id": reference_id,
        }

    aggregated: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        proto = rec.get("protocol", "UNKNOWN")
        if proto not in aggregated:
            aggregated[proto] = {"total_bytes": 0, "total_packets": 0, "flow_count": 0}
        aggregated[proto]["total_bytes"] += rec.get("bytes", 0)
        aggregated[proto]["total_packets"] += rec.get("packets", 0)
        aggregated[proto]["flow_count"] += 1

    total_bytes = sum(v["total_bytes"] for v in aggregated.values())
    ranked = sorted(aggregated.items(), key=lambda x: x[1]["total_bytes"], reverse=True)

    breakdown = []
    for proto, stats in ranked:
        breakdown.append({
            "protocol": proto,
            "total_bytes": stats["total_bytes"],
            "total_packets": stats["total_packets"],
            "flow_count": stats["flow_count"],
            "pct_bytes": round(stats["total_bytes"] / total_bytes * 100, 1) if total_bytes else 0,
        })

    return {
        "breakdown": breakdown,
        "total_bytes": total_bytes,
        "total_records_analysed": len(records),
        "reference_id": reference_id,
    }


@tool
def list_datasets(data_type: Optional[str] = None) -> Dict[str, Any]:
    """List all datasets currently stored in agent memory for this conversation.

    Returns lightweight metadata only — no data payloads. Useful for discovering
    what datasets are available before running analysis, or for auditing memory usage.

    Args:
        data_type: Optional filter by category label (e.g. "network_flows").
            Pass None (default) to list all stored datasets.

    Returns:
        Dictionary containing:
        - datasets (list): list of metadata dicts with reference_id, data_type,
          description, record_count, size_bytes, created_at
        - count (int): total number of datasets found

    Examples:
        >>> list_datasets()
        {"datasets": [{"reference_id": "a1b2c3d4", "record_count": 1000, ...}], "count": 1}

        >>> list_datasets(data_type="network_flows")
        {"datasets": [...], "count": 2}
    """
    entries = Memory().list_entries(data_type=data_type)

    datasets = [
        {
            "reference_id": e.get("reference_id"),
            "data_type": e.get("data_type"),
            "description": e.get("description"),
            "record_count": e.get("record_count"),
            "size_bytes": e.get("size_bytes"),
            "created_at": e.get("created_at"),
        }
        for e in entries
    ]

    return {"datasets": datasets, "count": len(datasets)}


@tool
def drop_dataset(reference_id: str) -> Dict[str, Any]:
    """Delete a stored dataset from agent memory.

    Use this to free up memory after analysis is complete, or to remove a
    dataset that is no longer needed. Deletion is immediate and permanent
    within the conversation.

    Args:
        reference_id: The 8-character ID of the dataset to delete.

    Returns:
        Dictionary with:
        - deleted (bool): True if deletion succeeded
        - reference_id (str): the ID that was deleted
        - error (str): present only if deletion failed

    Examples:
        >>> drop_dataset(reference_id="a1b2c3d4")
        {"deleted": True, "reference_id": "a1b2c3d4"}
    """
    try:
        Memory().delete(reference_id)
        return {"deleted": True, "reference_id": reference_id}
    except KeyError:
        return {
            "deleted": False,
            "reference_id": reference_id,
            "error": f"No dataset found for reference_id '{reference_id}'. "
                     "It may have already expired or been deleted.",
        }
