"""Triage tool for handoff-agent."""

from ncp import handoff, tool

URGENT_MARKERS = ("outage", "down", "critical", "urgent", "sev1", "sev-1", "unreachable")


@tool
def classify_request(query: str) -> dict:
    """Classify an incoming network request and route urgent ones to the incident specialist.

    Detects urgency from keywords like "outage", "down", "critical", "urgent",
    "sev1"/"sev-1", "unreachable" (case-insensitive) and hands off to the
    incident_specialist agent when found.

    Args:
        query: The user's request, verbatim

    Returns:
        A dict with 'query' and 'priority' ("urgent" or "normal")
    """
    priority = "urgent" if any(marker in query.lower() for marker in URGENT_MARKERS) else "normal"
    if priority == "urgent":
        handoff("incident_specialist", reason=f"urgent request: {query!r}")
    return {"query": query, "priority": priority}
