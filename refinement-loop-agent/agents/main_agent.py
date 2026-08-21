"""Main agent definition for refinement-loop-agent.

Demonstrates LoopAgent + StopCondition: the generator-critic pattern, where a
draft is repeatedly revised until a reviewer approves it (or the loop hits its
iteration cap).

    ┌─────────────────────────────────────────────┐
    │  draft_change_plan   ──▶  state["plan"]     │
    │  review_change_plan  ──▶  state["review_status"]
    └────────── repeat while status != "approved" ┘
                          ↓
                present_change_plan  (streams the approved plan)

Two things make this work:

**Self-referential state.** On pass 2 and later, `draft_change_plan` needs to see
the draft *it* produced last pass, plus the reviewer's objections. A step can
always read its own `output_key` from the previous iteration - that's true even
with `share_state=False`, because a step reading its own prior output isn't
"seeing unrelated history", it's the whole basis of iterative refinement. Here
`share_state=True` is set anyway, so the drafter can also read `{review_status}`,
which is a *different* step's output.

**Declarative stopping.** `StopCondition(state_key="review_status",
equals="approved")` is checked after each pass. It's plain data rather than a
callable so it survives `ncp deploy` serialization like every other field.

**Why the presenter step exists.** A loop can't stream its answer: whether a pass
is the final one is only known after the stop condition is evaluated, and chat
output is append-only, so streaming every pass would pile all the drafts on top
of each other. Putting the loop inside a SequentialAgent with a presenter step
after it makes the presenter the last step - so its output is what streams back,
token by token.
"""

from ncp import (
    Agent,
    AgentTool,
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
# The refinement loop
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


change_planning_workflow = SequentialAgent(
    name="change_planning_workflow",
    description="Refines a change plan until it passes review, then presents it",
    sub_agents=[refinement_loop, present_change_plan],
)


# =============================================================================
# The deployable agent
# =============================================================================

agent = Agent(
    name="change_planner",
    description="Produces review-passing network change plans via an iterative drafting loop",
    instructions="""You help network engineers write change plans that will pass
change-management review.

When the user describes a change they want to make (upgrade firmware, modify
ACLs, replace hardware, etc.), call change_planning_workflow with their request.
It drafts a plan, reviews it against the standards, revises it as needed, and
returns the approved version. Present that plan.

If the user just wants to know what the standards are, call
get_change_standards and answer directly.""",
    tools=[
        get_change_standards,
        AgentTool(
            change_planning_workflow,
            name="change_planning_workflow",
            description=(
                "Draft a network change plan, refine it until it passes "
                "change-management review, and return the approved plan."
            ),
        ),
    ],
)
