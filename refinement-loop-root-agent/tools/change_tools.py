"""Change-planning and review tools for the refinement loop example."""

from ncp import tool

# Phrases that make a change plan risky enough to send back for revision.
_RISKY_PATTERNS = {
    "no rollback": "no rollback procedure is described",
    "reload": "a device reload is proposed without a maintenance window",
    "all devices": "the change targets all devices at once instead of in stages",
    "fleet-wide": "the change targets the whole fleet at once instead of in stages",
    "during business hours": "the change runs during business hours",
    "skip validation": "validation steps are skipped",
}

_CHANGE_STANDARDS = [
    "Stage changes: one canary device, then one site, then the rest",
    "Every plan needs an explicit rollback procedure with concrete commands",
    "Reloads and disruptive changes require a named maintenance window",
    "Include pre-change and post-change validation commands",
    "State the blast radius: which sites and how many devices are affected",
]


@tool
def get_change_standards() -> dict:
    """Retrieve the organization's change-management standards.

    Returns:
        A dict with the list of standards every change plan must satisfy.
    """
    return {"standards": _CHANGE_STANDARDS}


@tool
def review_change_plan(plan: str) -> dict:
    """Review a change plan against the change-management standards.

    Args:
        plan: The full text of the proposed change plan

    Returns:
        A dict with 'verdict' ("approved" or "needs_revision") and, when it
        needs revision, the list of 'problems' to fix.
    """
    lowered = plan.lower()
    problems = [
        reason for phrase, reason in _RISKY_PATTERNS.items() if phrase in lowered
    ]

    # A plan with no rollback wording at all is treated as missing one.
    if "rollback" not in lowered:
        problems.append("no rollback procedure is described")

    verdict = "approved" if not problems else "needs_revision"
    return {
        "verdict": verdict,
        "problems": sorted(set(problems)),
        "standards_checked": len(_CHANGE_STANDARDS),
    }
