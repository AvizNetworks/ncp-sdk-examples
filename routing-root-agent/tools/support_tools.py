"""Specialist tools for the routed support desk."""

from ncp import tool

_INVOICES = {
    "ACME-2291": {"amount_usd": 18400.00, "status": "overdue", "days_overdue": 12},
    "ACME-2304": {"amount_usd": 6200.00, "status": "paid", "days_overdue": 0},
}

_KB = {
    "vpn": [
        "Confirm the tunnel's phase-1 and phase-2 lifetimes match on both peers",
        "Check that the pre-shared key has not rotated on one side only",
        "Verify NAT-T is enabled if either peer sits behind NAT",
    ],
    "wifi": [
        "Check controller channel utilization on the reported band",
        "Confirm the SSID's RADIUS server is reachable from the AP's VLAN",
        "Look for rogue AP interference on overlapping channels",
    ],
    "latency": [
        "Compare hop-by-hop latency against the last known-good traceroute",
        "Check interface queue drops along the path",
        "Confirm no recent route change moved traffic to a longer path",
    ],
}


@tool
def look_up_invoice(invoice_id: str) -> dict:
    """Look up an invoice's amount and payment status.

    Args:
        invoice_id: The invoice reference, e.g. "ACME-2291"

    Returns:
        A dict with the invoice's amount, status, and days overdue, or an
        'error' key if it isn't found.
    """
    record = _INVOICES.get(invoice_id.upper())
    if record is None:
        return {"error": f"No invoice found with ID {invoice_id!r}"}
    return {"invoice_id": invoice_id.upper(), **record}


@tool
def search_kb(topic: str) -> dict:
    """Search the technical knowledge base for troubleshooting steps.

    Args:
        topic: A short topic keyword, e.g. "vpn", "wifi", "latency"

    Returns:
        A dict with the matched topic and its troubleshooting steps, or the
        list of available topics if there's no match.
    """
    key = topic.strip().lower()
    for known, steps in _KB.items():
        if known in key:
            return {"topic": known, "steps": steps}
    return {
        "error": f"No knowledge base article for {topic!r}",
        "available_topics": sorted(_KB),
    }
