"""Diagnostic tools for hooks-agent, plus the shared execution-event log.

AgentHooks callbacks run wherever the agent executes; their print()/logging
output isn't surfaced back to `ncp playground`. So instead of printing,
the hooks registered in agents/main_agent.py append a line to
`execution_log` below, and get_execution_log() reads it back through the
chat itself.
"""

import random
from datetime import datetime, timezone
from typing import List

from ncp import tool

execution_log: List[str] = []


def log_event(line: str) -> None:
    """Append a timestamped line to the shared execution log."""
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    execution_log.append(f"[{timestamp}] {line}")


UNREACHABLE_MARKERS = ("down", "offline", "unreachable")


@tool
def check_device_health(hostname: str) -> dict:
    """Check the health of a network device.

    Simulates a health check against a device. Any hostname containing
    "down", "offline", or "unreachable" (case-insensitive) simulates an
    unreachable device and raises an error - ask about one of those to see
    the on_tool_execution_error hook fire.

    Args:
        hostname: The device hostname or IP to check, e.g. "switch-core-1"

    Returns:
        A dict with hostname, status, cpu_percent, and memory_percent
    """
    if any(marker in hostname.lower() for marker in UNREACHABLE_MARKERS):
        raise ConnectionError(f"Device '{hostname}' did not respond to health check")

    random.seed(hostname)
    return {
        "hostname": hostname,
        "status": "healthy",
        "cpu_percent": random.randint(5, 60),
        "memory_percent": random.randint(20, 70),
    }


@tool
def get_execution_log(clear: bool = False) -> dict:
    """Return the log of agent-execution events captured by AgentHooks so far.

    Every hook wired up on this agent (agent start/complete, each
    iteration, each LLM call, each tool call) appends one line here as it
    fires. Call this to see the full lifecycle of the current run.

    Args:
        clear: If True, clear the log after reading it

    Returns:
        A dict with 'entries' (list of log lines, oldest first) and 'count'
    """
    entries = list(execution_log)
    if clear:
        execution_log.clear()
    return {"entries": entries, "count": len(entries)}
