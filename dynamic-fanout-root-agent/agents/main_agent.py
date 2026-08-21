"""Main agent definition for dynamic-fanout-root-agent.

Demonstrates deploying the *enclosing* `SequentialAgent` of a runtime-sized
fan-out as the entry point itself, instead of wrapping it as a tool behind a
plain `Agent` (compare `dynamic-fanout-agent`, which does the latter).

Here the constraint is stronger than in `parallel-fanout-root-agent`: a
`DynamicParallelAgent` cannot be a deployment root *at all*, bare or
otherwise - by design, not just by convention. `DynamicParallelAgent.
items_from_state` reads a state key an *earlier sibling step in the same
pipeline* wrote (here, the planner's JSON list of sites). There is no earlier
sibling to have written that key unless a `DynamicParallelAgent` is running as
a step inside a `SequentialAgent`/`LoopAgent` pass - which is exactly what
disqualifies it from ever being the outermost node on its own.

So the entry point here is `site_audit_workflow` - the three-step
`SequentialAgent` that already contains the planner, the fan-out, and the
summarizer - not `audit_all_planned_sites` in isolation:

    plan_audit_scope  ──▶ state["audit_scope"]  (JSON list of site names)
              │
              ▼
    audit_all_planned_sites  (DynamicParallelAgent, sized by that list)
              │
              ▼
    summarize_audit  ──▶ this IS the answer

`ncp.toml` points straight at the whole pipeline:

    entry_point = "agents.main_agent:site_audit_workflow"

instead of

    entry_point = "agents.main_agent:agent"
"""

from ncp import (
    Agent,
    DynamicParallelAgent,
    SequentialAgent,
)
from tools.audit_tools import audit_site, list_sites


# =============================================================================
# Step 1: Plan - decide which sites are in scope, as a JSON list
# =============================================================================

plan_audit_scope = Agent(
    name="plan_audit_scope",
    description="Decides which sites an audit request covers",
    instructions="""You decide which sites a compliance audit should cover.

Call list_sites to see every site with its region, tier, and device count. Then
work out which ones the user's request covers:
- "everything" / "all sites" -> every site
- "datacenters" -> every site whose tier is datacenter
- "branches" -> every site whose tier is branch
- a region name (us-east, us-west, eu-central) -> every site in that region
- specific site names -> just those

Respond with ONLY a JSON array of site name strings, nothing else. No prose, no
markdown fences, no explanation.

Correct: ["dc-east", "dc-west", "dc-fra"]
Wrong:   Here are the sites: ["dc-east"]""",
    tools=[list_sites],
    # DynamicParallelAgent reads this key to size the fan-out.
    output_key="audit_scope",
)


# =============================================================================
# The template - replicated once per planned site
# =============================================================================

site_auditor = Agent(
    name="site_auditor",
    description="Audits a single site for compliance findings",
    instructions="""You audit one site for compliance problems.

Your input is a site name. Call audit_site with it and report:
- the site name and how many devices it has
- each finding as its own bullet
- a severity for the site overall: CLEAN (no findings), MINOR, or MAJOR
  (anything involving default credentials, EOL firmware, or unrestricted access)

Be brief - a later step aggregates these into one report.""",
    tools=[audit_site],
)


# =============================================================================
# Fan-out sized at runtime by the planner's output - CANNOT be a root on its
# own; see the module docstring for why.
# =============================================================================

audit_all_planned_sites = DynamicParallelAgent(
    name="audit_all_planned_sites",
    description="Audits every site the planner selected, concurrently",
    template=site_auditor,
    # The state key the planner wrote its JSON list to.
    items_from_state="audit_scope",
    # Branch i is recorded as "site_audit_0", "site_audit_1", ...
    item_output_key_prefix="site_audit",
    # Be a good citizen against the backing systems: audit at most 3 sites at
    # once, however many the planner selected.
    max_concurrency=3,
)


# =============================================================================
# Step 3: Aggregate the per-site audits into one report
# =============================================================================

summarize_audit = Agent(
    name="summarize_audit",
    description="Aggregates per-site audit results into one compliance report",
    instructions="""You write compliance audit reports.

Your input is a JSON object mapping site_audit_N keys to that site's audit
result. Write a report with:

- **Scope** - how many sites were audited
- **Findings by severity** - MAJOR sites first, then MINOR, then CLEAN. One line
  per site with its most important finding
- **Top priority** - the single finding to fix first, and why

If every site is CLEAN, say so plainly instead of padding the report.""",
)


# =============================================================================
# The pipeline - this is the deployable entry point, not a plain Agent
# =============================================================================
# No wrapping Agent, no AgentTool: `ncp.toml`'s entry_point names this object
# directly. audit_all_planned_sites itself can never be the entry point - see
# the module docstring for why a DynamicParallelAgent can't stand alone.

site_audit_workflow = SequentialAgent(
    name="site_audit_workflow",
    description="Plans an audit's scope, audits each site concurrently, then reports",
    sub_agents=[plan_audit_scope, audit_all_planned_sites, summarize_audit],
)
