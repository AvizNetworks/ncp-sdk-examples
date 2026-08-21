"""Main agent definition for parallel-fanout-agent.

Demonstrates ParallelAgent + AgentInvocation: running the *same* specialist
agent several times concurrently, each with a different task, then synthesizing
the gathered results.

The shape is fan-out/gather:

    ParallelAgent  ─┬─▶ region_health_agent("us-east")    ──┐
                    ├─▶ region_health_agent("us-west")    ──┼─▶ merged results
                    └─▶ region_health_agent("eu-central") ──┘
                                     ↓
                              synthesize_health  (reads the merged dict)

**Why AgentInvocation is needed.** An agent's tools must have unique names, and
that includes AgentTool-wrapped sub-agents - so you cannot put the same agent in
a tools list three times. AgentInvocation solves this by living in `sub_agents`
instead: it wraps a node to override the input (`query`) and result name
(`output_key`) for that one slot, so one agent object can appear as many times
as you like, each doing different work.

Compare with `dynamic-fanout-agent`, where the *number* of branches isn't known
until runtime.
"""

from ncp import (
    Agent,
    AgentInvocation,
    AgentTool,
    ParallelAgent,
    SequentialAgent,
)
from tools.region_tools import get_region_health, list_regions


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
# prose - so it feeds a synthesizer step rather than answering the user itself.

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


regional_health_check = SequentialAgent(
    name="regional_health_check",
    description="Checks all regions concurrently, then summarizes fleet health",
    sub_agents=[check_all_regions, synthesize_health],
)


# =============================================================================
# The deployable agent
# =============================================================================

agent = Agent(
    name="fleet_health_monitor",
    description="Reports network health across all regions using a concurrent fan-out check",
    instructions="""You report on network fleet health across regions.

When the user asks about overall/fleet/all-region health, call
regional_health_check - it checks every region at once and returns a synthesized
summary. Present that summary to the user.

For a question about one specific region, or to list which regions exist, use
list_regions and answer directly rather than running the full fan-out.""",
    tools=[
        list_regions,
        AgentTool(
            regional_health_check,
            name="regional_health_check",
            description=(
                "Check the health of every region concurrently and return one "
                "synthesized fleet-wide summary."
            ),
        ),
    ],
)
