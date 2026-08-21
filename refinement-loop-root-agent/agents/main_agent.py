"""Main agent definition for refinement-loop-root-agent.

Demonstrates deploying the *enclosing* `SequentialAgent` of a generator-critic
refinement loop as the entry point itself, instead of wrapping it as a tool
behind a plain `Agent` (compare `refinement-loop-agent`, which does the
latter).

Here the constraint is about *streaming*, not standalone execution the way it
was for `DynamicParallelAgent` (`dynamic-fanout-root-agent`) or usefulness the
way it was for `ParallelAgent` (`parallel-fanout-root-agent`). A `LoopAgent`
runs each pass sequentially and CAN run as a standalone node just fine - the
problem is that which pass is the *last* one is only known after that pass's
stop condition is checked, and the chat stream is append-only. So a
`LoopAgent`'s own text is never streamed live, pass or no pass - its result is
only available once the whole loop finishes. That means a `LoopAgent` can
never itself be the step whose text reaches the user; something has to run
after it and stream instead.

So the entry point here is `change_planning_workflow` - the `SequentialAgent`
that already puts a presenter step after the loop - not `refinement_loop` in
isolation:

    refinement_loop  (LoopAgent: draft, review, repeat until approved)
              │
              ▼
    present_change_plan  ──▶ this IS the answer

`ncp.toml` points straight at the whole pipeline:

    entry_point = "agents.main_agent:change_planning_workflow"

instead of

    entry_point = "agents.main_agent:agent"
"""

from ncp import (
    Agent,
    LoopAgent,
    SequentialAgent,
    StopCondition,
)
from tools.change_tools import get_change_standards, review_change_plan


# =============================================================================
# The generator - reads its OWN previous draft plus the reviewer's objections
# =============================================================================

draft_change_plan = Agent(
    name="draft_change_plan",
    description="Drafts (and re-drafts) a network change plan",
    instructions="""You draft network change plans.

Call get_change_standards first so you know what the plan must satisfy.

Your previous draft, if you have made one, was:

{plan}

The reviewer's verdict on it was:

{review_status}

If there is a previous draft and the reviewer rejected it, produce a REVISED
plan that fixes every problem the reviewer listed - do not start over, and do
not repeat mistakes they already flagged. If there is no previous draft, write
the first one.

Every plan must have: Summary, Blast Radius, Staged Rollout, Validation
Commands, and an explicit Rollback Procedure with concrete commands.

Output only the plan.""",
    tools=[get_change_standards],
    # The drafter reads this same key back on the next pass - that's the
    # self-referential state that makes refinement possible.
    output_key="plan",
)


# =============================================================================
# The critic - its verdict is what the stop condition watches
# =============================================================================

review_plan = Agent(
    name="review_plan",
    description="Reviews a change plan against change-management standards",
    instructions="""You review network change plans against the standards.

Call review_change_plan with the full plan text you were given.

If the verdict is "approved", reply with exactly:
approved

If it is "needs_revision", reply with exactly the word on the first line:
needs_revision
then list each problem the tool reported as a bullet, so the drafter can fix
them on the next pass.

Never invent problems the tool did not report.""",
    tools=[review_change_plan],
    # The StopCondition below watches this key.
    output_key="review_status",
)


# =============================================================================
# The refinement loop - CANNOT be a root on its own; see the module docstring
# for why (its text is never the one that streams).
# =============================================================================

refinement_loop = LoopAgent(
    name="refinement_loop",
    description="Drafts and reviews a change plan until the review passes",
    sub_agents=[draft_change_plan, review_plan],
    # Cap the passes: without this a plan the reviewer keeps rejecting would
    # loop until the ceiling. 4 is enough for a plan to converge in practice.
    max_iterations=4,
    # Declarative, not a callable, so it survives deploy serialization.
    stop_on=StopCondition(state_key="review_status", equals="approved"),
    # Lets the drafter read {review_status} - a *different* step's output.
    # Reading its own {plan} would work without this.
    share_state=True,
)


# =============================================================================
# The presenter - the pipeline's last step, so its answer streams to the user
# =============================================================================

present_change_plan = Agent(
    name="present_change_plan",
    description="Presents the finished change plan to the user",
    instructions="""You present a finished network change plan.

Your input is the result of a drafting-and-review loop. Present the final plan
cleanly and in full, then add one short closing line saying it passed
change-management review.

Do not summarize the plan away - the user needs the whole thing, including the
rollback procedure.""",
)


# =============================================================================
# The pipeline - this is the deployable entry point, not a plain Agent
# =============================================================================
# No wrapping Agent, no AgentTool: `ncp.toml`'s entry_point names this object
# directly. refinement_loop itself can never be the entry point - see the
# module docstring for why a LoopAgent's own text never streams to the user.

change_planning_workflow = SequentialAgent(
    name="change_planning_workflow",
    description="Refines a change plan until it passes review, then presents it",
    sub_agents=[refinement_loop, present_change_plan],
)
