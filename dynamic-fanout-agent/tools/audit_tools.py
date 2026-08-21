"""Per-site audit tools for the runtime-sized fan-out example."""

from ncp import tool

_SITES = {
    "hq-campus": {"devices": 312, "region": "us-east", "tier": "campus"},
    "dc-east": {"devices": 148, "region": "us-east", "tier": "datacenter"},
    "dc-west": {"devices": 131, "region": "us-west", "tier": "datacenter"},
    "branch-sfo": {"devices": 24, "region": "us-west", "tier": "branch"},
    "branch-nyc": {"devices": 31, "region": "us-east", "tier": "branch"},
    "dc-fra": {"devices": 97, "region": "eu-central", "tier": "datacenter"},
}

_FINDINGS = {
    "hq-campus": ["17 devices running an EOL firmware release", "SNMPv2 still enabled on 4 switches"],
    "dc-east": ["TACACS fallback to local auth enabled fleet-wide"],
    "dc-west": [],
    "branch-sfo": ["Default SNMP community string on 1 device"],
    "branch-nyc": ["No config backup recorded in 94 days"],
    "dc-fra": ["3 devices with unrestricted VTY access lists", "NTP unauthenticated"],
}


@tool
def list_sites() -> dict:
    """List every auditable site with its region, tier, and device count.

    Returns:
        A dict with a 'sites' list of {name, region, tier, devices} entries.
    """
    return {
        "sites": [
            {"name": name, **meta} for name, meta in sorted(_SITES.items())
        ]
    }


@tool
def audit_site(site: str) -> dict:
    """Run a compliance audit against one site.

    Args:
        site: Site name, e.g. "hq-campus", "dc-fra"

    Returns:
        A dict with the site's findings list and device count, or an 'error'
        key if the site is unknown.
    """
    key = site.strip().lower()
    if key not in _SITES:
        return {"error": f"Unknown site {site!r}", "known_sites": sorted(_SITES)}
    findings = _FINDINGS.get(key, [])
    return {
        "site": key,
        "devices": _SITES[key]["devices"],
        "finding_count": len(findings),
        "findings": findings,
    }
