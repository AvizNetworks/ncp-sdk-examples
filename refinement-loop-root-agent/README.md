# Refinement Loop Root Agent - Deploying a Generator-Critic Loop's `SequentialAgent` as the Entry Point

**Demonstrates deploying the *enclosing* `SequentialAgent` of a `LoopAgent` refinement loop as the entry point itself - and why the `LoopAgent` step can never be the one whose text reaches the user.**

---

## 🎯 What This Example Teaches

1. **The general root mechanism, applied again.** Same as `sequential-pipeline-root-agent`: `ncp.toml`'s `entry_point` names a workflow composition node directly, skipping the wrapping `Agent`/`AgentTool`.
2. **A `LoopAgent`-specific rule, about streaming rather than execution.** A `LoopAgent` runs perfectly well as a standalone node - unlike a `DynamicParallelAgent` (`dynamic-fanout-root-agent`), it has no earlier-sibling dependency. What it can't do is stream: which pass is the *last* one is only known after that pass's stop condition is checked, so its own text is never what reaches the user, deployed bare or not.
3. **What "root" means here, concretely.** The entry point is `change_planning_workflow` - the two-step `SequentialAgent` that already puts a presenter after the loop - not `refinement_loop` on its own.

---

## 📁 Project Structure

```
refinement-loop-root-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 drafter + critic + loop + presenter - no wrapping Agent
└── tools/
    ├── __init__.py
    └── change_tools.py          # 🔧 get_change_standards, review_change_plan
```

---

## 🔗 The Pipeline: `agents/main_agent.py`

```python
from ncp import Agent, LoopAgent, SequentialAgent, StopCondition

draft_change_plan = Agent(..., instructions="...{plan}...{review_status}...", output_key="plan")
review_plan        = Agent(..., tools=[review_change_plan], output_key="review_status")

refinement_loop = LoopAgent(
    sub_agents=[draft_change_plan, review_plan],
    max_iterations=4,
    stop_on=StopCondition(state_key="review_status", equals="approved"),
    share_state=True,
)

present_change_plan = Agent(..., instructions="...present the finished plan in full...")

change_planning_workflow = SequentialAgent(
    sub_agents=[refinement_loop, present_change_plan],
)
```

This is unchanged from `refinement-loop-agent` - see that example's README for
how self-referential state (`{plan}`) and `share_state` (`{review_status}`)
work together to make iterative revision possible. What's different here is
what deploys, and why it has to be `change_planning_workflow` rather than
`refinement_loop`.

### Why the entry point can't be the bare `LoopAgent`

```toml
# ncp.toml
[build]
entry_point = "agents.main_agent:change_planning_workflow"
```

A `LoopAgent` repeats a pass of steps until a `StopCondition` passes or
`max_iterations` is hit. Whether a given pass is the *last* one is only
knowable *after* that pass finishes and the stop condition is checked - and
the chat stream is append-only, with no "replace what I just streamed" event.
Streaming every pass's draft as it's produced would visibly pile all the
drafts on top of each other in the chat. So a `LoopAgent`'s result is only
ever available as a finished value once the whole loop completes - never as
something that streams live, no matter where in the workflow it sits.

That is a different kind of constraint than `dynamic-fanout-root-agent`'s (a
`DynamicParallelAgent` cannot run standalone *at all*) or
`parallel-fanout-root-agent`'s (a `ParallelAgent` runs standalone fine, its
result just isn't prose). A `LoopAgent` runs standalone without issue - the
loop in this example would execute correctly even deployed bare. It simply
never has an answer to hand back live, so `present_change_plan` - the
pipeline's actual last step - is what the user needs, always.

> **Try it:** ask this agent to plan a change. You'll see `refinement_loop`
> announced, then `draft_change_plan` and `review_plan` alternate silently
> pass after pass (their drafts don't stream - by design, see above) until the
> review passes, and only then does `present_change_plan` stream back the
> finished plan.

---

## 🚀 Try It Out

```bash
cd refinement-loop-root-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy refinement-loop-root-agent.ncp
ncp playground --agent change_planning_workflow --show-tools
```

### Example: Drafting a change plan

**You**: I need to upgrade firmware on all our switches this weekend

**Agent**: `refinement_loop` drafts a plan, reviews it, and revises it (likely
flagging the "all... switches" staging problem on the first pass) until it
passes review; `present_change_plan` then streams back the approved plan in
full, including its rollback procedure.

---

## 🎓 Key Takeaways

- `ncp.toml`'s `entry_point` can name any workflow composition node, including one nested inside another - what matters is that the *outermost* node's last-executed step is a plain `Agent` producing prose
- A `LoopAgent` can run standalone just fine - it simply can never be that last-executed producer step, because which pass is final is only known after the fact
- Compare the three "why not the inner node" reasons across this set: `DynamicParallelAgent` can't execute standalone at all, `ParallelAgent` executes standalone but produces non-prose, `LoopAgent` executes standalone but can't stream

## 🚀 Next Steps

- Compare with `dynamic-fanout-root-agent` and `parallel-fanout-root-agent` for the other two reasons an inner workflow node isn't a valid root
- Compare with `routing-root-agent`, where the inner node (`RoutingAgent`) genuinely *can* be the bare root - one specialist, chosen once, is always the terminal producer
