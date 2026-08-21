"""Batch backup tool for streaming-status-agent.

Demonstrates send_status() (replace-in-place progress) and send_content()
(append-only partial output) from inside a single long-running tool.
"""

import asyncio
from datetime import datetime, timezone
from typing import List

from ncp import send_content, send_status, tool

stream_log: List[str] = []


def log_stream_event(line: str) -> None:
    """Append a timestamped line to the shared stream log (written by AgentHooks)."""
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    stream_log.append(f"[{timestamp}] {line}")


@tool
async def backup_devices(hostnames: List[str]) -> dict:
    """Back up configuration for a list of network devices, reporting progress as it goes.

    For each device this calls send_status() with overall progress
    ("Backing up switch-2 (2/5)...") and send_content() with a one-line
    result for that device, so the UI can show live progress instead of
    staying blank until every device finishes.

    Args:
        hostnames: List of device hostnames to back up, e.g. ["switch-1", "switch-2"]

    Returns:
        A dict with 'backed_up' (count) and 'results' (per-device outcome)
    """
    results = []
    total = len(hostnames)
    for i, host in enumerate(hostnames, start=1):
        await send_status(f"Backing up {host} ({i}/{total})...")
        await asyncio.sleep(1.5)  # simulate the backup taking a moment
        size_kb = 12 + (len(host) * 3) % 40
        await send_content(f"- {host}: backup complete ({size_kb} KB)\n")
        results.append({"hostname": host, "status": "success", "size_kb": size_kb})

    await send_status(f"Backup complete: {total}/{total} devices")
    return {"backed_up": total, "results": results}


@tool
def get_stream_log(clear: bool = False) -> dict:
    """Return the log of status/content events captured by AgentHooks so far.

    Every send_status()/send_content() call made by backup_devices fires an
    AgentHooks callback (on_status_update / on_tool_stream) that appends one
    line here, so you can see the full stream even if your client doesn't
    render live status/streaming events.

    Args:
        clear: If True, clear the log after reading it

    Returns:
        A dict with 'entries' (list of log lines, oldest first) and 'count'
    """
    entries = list(stream_log)
    if clear:
        stream_log.clear()
    return {"entries": entries, "count": len(entries)}
