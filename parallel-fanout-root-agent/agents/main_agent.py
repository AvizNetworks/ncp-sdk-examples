"""Main agent definition for parallel-fanout-root-agent.

Demonstrates deploying the *enclosing* `SequentialAgent` of a fan-out/gather
pipeline as the entry point itself, instead of wrapping it as a tool behind a
plain `Agent` (compare `parallel-fanout-agent`, which does the latter).

Unlike `sequential-pipeline-root-agent` and `routing-root-agent`, the bare
`ParallelAgent` step (`check_all_regions`) is deliberately NOT what gets
deployed here. A `ParallelAgent`'s own result is a merged
`{output_key: text}` mapping - useful as input to the next step, not
something to hand a user as an answer. Concretely: three branches run
concurrently, and only one step can ever be "the terminal producer" whose
text streams to the chat, so a synthesis step is what turns "three regions'
raw findings" into one fleet-wide answer - it isn't optional plumbing, it's
what makes the result presentable at all.

So the entry point here is `regional_health_check` - the `SequentialAgent`
that already wraps the fan-out with that synthesis step - not
`check_all_regions` on its own:

    check_all_regions (ParallelAgent, 3 concurrent branches) ──▶ synthesize_health
                                                                        ↓
                                                          this IS the answer

`ncp.toml` points straight at it:

    entry_point = "agents.main_agent:regional_health_check"

instead of

    entry_point = "agents.main_agent:agent"

That's the same trade `sequential-pipeline-root-agent` makes (no triage: every
message runs the full fan-out-and-synthesize, unconditionally), plus a second,
`ParallelAgent`-specific rule this example exists to make concrete: a
`ParallelAgent` needs a producer step after it before it can be a deployment's
terminal answer - bare or wrapped, that never changes.
"""

from ncp import (
    Agent,
    AgentInvocation,
    ParallelAgent,
    SequentialAgent,
)
from tools.region_tools import get_region_health


# =============================================================================
# The specialist that gets fanned out - defined ONCE, invoked three times
# =============================================================================

region_health_agent = Agent(
    name="region_health_agent",
    description="Assesses the health of a single network region",
    instructions="""You assess the health of one network region.

Your input names the region to check. Call get_region_health with that region
name, then report in three or four lines:
- how many devices are down, out of the total
- the 24h interface error count, and whether it looks normal or elevated
- any operator notes worth escalating

Finish with a one-word verdict on its own line: HEALTHY, DEGRADED, or CRITICAL.""",
    tools=[get_region_health],
)


# =============================================================================
# Fan-out: the same agent, three concurrent invocations, three result keys
# =============================================================================

check_all_regions = ParallelAgent(
    name="check_all_regions",
    description="Checks every region's health concurrently",
    sub_agents=[
        AgentInvocation(
            agent=region_health_agent,
            query="Assess the health of region: us-east",
            output_key="us_east_health",
        ),
        AgentInvocation(
            agent=region_health_agent,
            query="Assess the health of region: us-west",
            output_key="us_west_health",
        ),
        AgentInvocation(
            agent=region_health_agent,
            query="Assess the health of region: eu-central",
            output_key="eu_central_health",
        ),
    ],
)


# =============================================================================
# Gather: turn the merged per-region results into one fleet-wide answer
# =============================================================================
# A ParallelAgent's own output is a merged {output_key: text} mapping, not
# prose - so it feeds this synthesizer step rather than answering the user
# itself. This step is what lets regional_health_check be deployed as root at
# all: it is the pipeline's last step, so ITS text is what streams to the user.

synthesize_health = Agent(
    name="synthesize_health",
    description="Turns per-region health reports into one fleet-wide summary",
    instructions="""You write fleet-wide network health summaries.

Your input is a JSON object mapping region keys (us_east_health, us_west_health,
eu_central_health) to that region's health report.

Write a short summary that:
1. Opens with the overall fleet verdict - the worst single region's verdict wins
2. Gives one line per region with its verdict and the single most important fact
3. Ends with "Attention needed:" and the regions that are not HEALTHY, most
   severe first. If everything is healthy, say so instead.""",
)


# =============================================================================
# The pipeline - this is the deployable entry point, not a plain Agent
# =============================================================================
# No wrapping Agent, no AgentTool: `ncp.toml`'s entry_point names this object
# directly. check_all_regions itself is never the entry point - see the module
# docstring for why a bare ParallelAgent can't be one.

regional_health_check = SequentialAgent(
    name="regional_health_check",
    description="Checks all regions concurrently, then summarizes fleet health",
    sub_agents=[check_all_regions, synthesize_health],
)
