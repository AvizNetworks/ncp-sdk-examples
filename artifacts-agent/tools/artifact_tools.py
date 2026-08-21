"""Tools for artifacts-agent.

Demonstrates Artifacts().save_text() / save_file() / get_metadata():
registering downloadable, non-tabular files (a markdown report, a diagram
the agent wrote to its own local filesystem) - the counterpart to
Memory(exportable=True) and its export_data_from_memory UI card (see
ncp-sdk-examples/memory-export-agent), which only handle tabular
list[dict] records.
"""

import os
import random
import tempfile
from typing import Any, Dict, List

from ncp import Artifacts, Memory, tool

_STATUSES = ["healthy", "healthy", "healthy", "degraded", "unreachable"]
_ROLES = ["core-switch", "edge-router", "access-switch", "firewall"]


def _generate_health_rows(count: int) -> List[Dict[str, Any]]:
    rows = []
    for i in range(1, count + 1):
        rows.append({
            "hostname": f"device-{i:03d}",
            "role": random.choice(_ROLES),
            "status": random.choice(_STATUSES),
            "cpu_percent": random.randint(5, 95),
        })
    return rows


@tool
def collect_device_health(count: int = 15) -> Dict[str, Any]:
    """Collect synthetic per-device health data and store it in agent memory.

    Simulates what a real monitoring tool would return. Stored via
    Memory().store(..., exportable=False) - this raw tabular data isn't meant
    for direct CSV/JSON download (see memory-export-agent for that); instead
    it's the input to generate_health_report, which turns it into a
    human-readable markdown artifact.

    Args:
        count: Number of device rows to generate (1-200)

    Returns:
        A dict with reference_id and record_count
    """
    count = max(1, min(count, 200))
    rows = _generate_health_rows(count)

    reference_id = Memory().store(
        data=rows,
        data_type="device_health",
        description=f"Device health snapshot ({count} devices)",
        exportable=False,
    )

    return {"reference_id": reference_id, "record_count": len(rows)}


@tool
def generate_health_report(reference_id: str, region: str = "us-west") -> Dict[str, Any]:
    """Turn a device health dataset already in agent memory into a
    downloadable markdown report.

    Demonstrates the "artifact built from data already in memory" path:
    retrieve the raw rows with Memory().retrieve(), render them as a
    markdown summary + table, then hand that text to Artifacts().save_text()
    so the user can download it as a .md file - something
    export_data_from_memory can't do, since it only serves the raw stored
    rows as CSV/JSON/Excel, not a rendered report.

    Args:
        reference_id: The reference_id returned by collect_device_health
        region: Label used in the report title/filename

    Returns:
        Dict with export_id, filename, download_url, download_link,
        file_size_bytes (as returned by Artifacts().save_text())
    """
    rows = Memory().retrieve(reference_id)

    healthy = sum(1 for r in rows if r["status"] == "healthy")
    degraded = sum(1 for r in rows if r["status"] == "degraded")
    unreachable = sum(1 for r in rows if r["status"] == "unreachable")

    lines = [
        f"# Device Health Report — {region}",
        "",
        f"- Total devices: {len(rows)}",
        f"- Healthy: {healthy}",
        f"- Degraded: {degraded}",
        f"- Unreachable: {unreachable}",
        "",
        "| Hostname | Role | Status | CPU % |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['hostname']} | {r['role']} | {r['status']} | {r['cpu_percent']} |"
        )
    markdown = "\n".join(lines)

    return Artifacts().save_text(
        markdown,
        filename=f"{region}_health_report.md",
        description=f"Device health report for {region} ({len(rows)} devices)",
    )


@tool
def generate_topology_diagram(region: str = "us-west") -> Dict[str, Any]:
    """Write a simple topology diagram to a local file and register it as a
    downloadable artifact.

    Demonstrates the "artifact created on the agent's own filesystem" path:
    a real tool might shell out to a diagram generator or draw an image with
    a library, ending up with a file already on disk. This example writes a
    small ASCII-art diagram instead, to keep the dependency footprint at
    zero, then hands the path to Artifacts().save_file() - the platform
    copies the bytes into its own managed storage and registers them the
    same way save_text()/save_bytes() do; the original temp file is ours to
    clean up afterward.

    Args:
        region: Label used in the diagram title/filename

    Returns:
        Dict with export_id, filename, download_url, download_link,
        file_size_bytes (as returned by Artifacts().save_file())
    """
    diagram = f"""Topology - {region}

                     [ core-switch-01 ]
                     /               \\
        [ edge-router-01 ]      [ edge-router-02 ]
             |                          |
     [ access-switch-01 ]      [ access-switch-02 ]
"""
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="topology_")
    with os.fdopen(fd, "w") as f:
        f.write(diagram)

    try:
        return Artifacts().save_file(
            path,
            filename=f"{region}_topology.txt",
            description=f"Network topology diagram for {region}",
        )
    finally:
        os.remove(path)


@tool
def get_artifact_info(export_id: int) -> Dict[str, Any]:
    """Look up metadata for a previously saved artifact without downloading it.

    Wraps Artifacts().get_metadata() - useful to confirm a file exists and
    check its size/type before telling the user it's ready.

    Args:
        export_id: The export_id returned by generate_health_report or
            generate_topology_diagram

    Returns:
        The metadata dict, or an 'error' key if the export_id is unknown
    """
    try:
        return Artifacts().get_metadata(export_id)
    except KeyError:
        return {
            "error": f"No artifact found for export_id '{export_id}'.",
            "export_id": export_id,
        }
