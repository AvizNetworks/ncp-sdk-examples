"""Incident lookup tools for the postmortem pipeline."""

from ncp import tool

_INCIDENTS = {
    "INC-4471": {
        "title": "Core switch spine-01 unreachable",
        "severity": "sev1",
        "duration_minutes": 47,
        "affected_sites": ["hq-campus", "dc-east"],
        "root_cause": "Power supply B failed; PSU-A had been faulty since a prior unnoticed alarm",
    },
    "INC-4482": {
        "title": "BGP session flapping to upstream ISP",
        "severity": "sev2",
        "duration_minutes": 132,
        "affected_sites": ["dc-west"],
        "root_cause": "MTU mismatch introduced by a change to the peering interface",
    },
}

_EVENTS = {
    "INC-4471": [
        ("02:14", "Monitoring alerts: spine-01 unreachable via ICMP and SNMP"),
        ("02:19", "On-call paged; confirmed both uplinks down from dc-east"),
        ("02:31", "Remote hands dispatched; PSU-B reported as failed on inspection"),
        ("02:58", "PSU-B replaced, spine-01 booted, adjacencies re-established"),
        ("03:01", "Traffic re-converged; monitoring green across both sites"),
    ],
    "INC-4482": [
        ("11:02", "BGP neighbor 203.0.113.9 flapping, 6 transitions in 5 minutes"),
        ("11:20", "Correlated with a change window touching the peering interface"),
        ("12:40", "MTU restored to 9216 on both ends; session stable"),
        ("13:14", "Monitoring confirms no further transitions"),
    ],
}


@tool
def get_incident(incident_id: str) -> dict:
    """Look up the summary record for an incident.

    Args:
        incident_id: The incident ticket ID, e.g. "INC-4471"

    Returns:
        A dict with the incident's title, severity, duration, affected sites,
        and root cause, or an 'error' key if the ID is unknown.
    """
    record = _INCIDENTS.get(incident_id.upper())
    if record is None:
        return {"error": f"No incident found with ID {incident_id!r}"}
    return {"incident_id": incident_id.upper(), **record}


@tool
def get_incident_events(incident_id: str) -> dict:
    """Retrieve the ordered event log recorded during an incident.

    Args:
        incident_id: The incident ticket ID, e.g. "INC-4471"

    Returns:
        A dict with 'incident_id' and a list of {time, event} entries in
        chronological order.
    """
    events = _EVENTS.get(incident_id.upper(), [])
    return {
        "incident_id": incident_id.upper(),
        "events": [{"time": t, "event": e} for t, e in events],
    }
