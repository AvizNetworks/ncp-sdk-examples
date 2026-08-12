"""Incident-response tools for the incident_specialist agent."""

from ncp import tool

_RUNBOOKS = {
    "link-down": [
        "Check the physical layer: cabling, SFP, port errors (show interface counters)",
        "Check the neighbor device's matching interface",
        "Review recent change history for the affected link",
        "Escalate to the on-call network engineer if unresolved in 15 minutes",
    ],
    "bgp-flap": [
        "Check BGP neighbor state and the last flap timestamp",
        "Look for interface flaps or MTU mismatches on the peering link",
        "Check for a route-limit or max-prefix-exceeded condition",
        "Escalate to the on-call network engineer if flapping continues",
    ],
}


@tool
def get_runbook(incident_type: str) -> dict:
    """Look up the response runbook for a given incident type.

    Args:
        incident_type: A short label for the incident, e.g. "link-down", "bgp-flap"

    Returns:
        A dict with 'incident_type' and ordered 'steps' to follow
    """
    steps = _RUNBOOKS.get(
        incident_type.lower().replace(" ", "-"),
        ["No specific runbook found - escalate to the on-call network engineer immediately"],
    )
    return {"incident_type": incident_type, "steps": steps}


@tool
def page_oncall(reason: str) -> dict:
    """Page the on-call network engineer.

    Args:
        reason: A short description of why on-call is being paged

    Returns:
        A dict confirming the page was sent, with an incident ticket ID
    """
    return {"paged": True, "reason": reason, "ticket_id": "INC-20260812-001"}
