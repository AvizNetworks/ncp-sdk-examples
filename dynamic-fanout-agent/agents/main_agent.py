"""Main agent definition for dynamic-fanout-agent.

Demonstrates DynamicParallelAgent: a fan-out whose *number of branches* is
decided at runtime rather than written into the code.

In `parallel-fanout-agent` the branches are fixed - three regions, three
AgentInvocation entries, decided when the workflow is written. That works when
you always check the same things. It doesn't work for "audit every datacenter"
or "audit the branch sites", where how many branches you need depends on what
the user asked for.

Here a planner step decides:

    plan_audit_scope  ──(JSON list of site names)──▶  state["audit_scope"]
                                                            ↓
    DynamicParallelAgent  reads that list and spins up one branch per entry
                                                            ↓
    summarize_audit  turns the merged per-site findings into one report

The planner writes a JSON list to its output_key; DynamicParallelAgent reads
that key via `items_from_state` and replicates its `template` agent once per
item, passing each item as that branch's input. Two sites means two branches;
six means six - no code change either way.

`items_from_state` is an explicit structural read the workflow author wired on
purpose, so unlike `{placeholder}` templating it does not need `share_state`.
The planner and the fan-out must be steps of the same pipeline, though - that's
how the fan-out can see what the planner just wrote.
"""

from ncp import (
    Agent,
    AgentTool,
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
# Fan-out sized at runtime by the planner's output
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


site_audit_workflow = SequentialAgent(
    name="site_audit_workflow",
    description="Plans an audit's scope, audits each site concurrently, then reports",
    sub_agents=[plan_audit_scope, audit_all_planned_sites, summarize_audit],
)


# =============================================================================
# The deployable agent
# =============================================================================

agent = Agent(
    name="compliance_auditor",
    description="Runs compliance audits across a runtime-determined set of sites",
    instructions="""You run network compliance audits.

When the user asks for an audit - of everything, of a tier ("the datacenters"),
of a region, or of named sites - call site_audit_workflow with their request
verbatim. It works out the scope itself, audits those sites concurrently, and
returns a single report. Present that report.

If the user just wants to know which sites exist, call list_sites and answer
directly.""",
    tools=[
        list_sites,
        AgentTool(
            site_audit_workflow,
            name="site_audit_workflow",
            description=(
                "Run a compliance audit. Pass the user's request verbatim - the "
                "workflow determines which sites are in scope on its own."
            ),
        ),
    ],
)
