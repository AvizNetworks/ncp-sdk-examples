# Parallel Fanout Root Agent - Deploying a Fan-Out/Gather Pipeline's `SequentialAgent` as the Entry Point

**Demonstrates deploying the *enclosing* `SequentialAgent` of a `ParallelAgent` fan-out/gather pipeline as the entry point itself - and why the `ParallelAgent` step alone can't be.**

---

## 🎯 What This Example Teaches

1. **The general root mechanism, applied again.** Same as `sequential-pipeline-root-agent`: `ncp.toml`'s `entry_point` names a workflow composition node directly, skipping the wrapping `Agent`/`AgentTool`.
2. **A `ParallelAgent`-specific rule.** Unlike `SequentialAgent` or `RoutingAgent`, a bare `ParallelAgent` is never the right thing to deploy as root - its own result is a merged `{output_key: text}` mapping, not an answer. It always needs a synthesis step after it, bare deployment or not.
3. **What "root" means here, concretely.** The entry point is `regional_health_check` - the two-step `SequentialAgent` that already wraps the fan-out with a synthesizer - not `check_all_regions` (the `ParallelAgent`) on its own.

---

## 📁 Project Structure

```
parallel-fanout-root-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 region_health_agent + fan-out + synthesizer - no wrapping Agent
└── tools/
    ├── __init__.py
    └── region_tools.py          # 🔧 get_region_health
```

---

## 🔗 The Pipeline: `agents/main_agent.py`

```python
from ncp import Agent, AgentInvocation, ParallelAgent, SequentialAgent

region_health_agent = Agent(..., tools=[get_region_health])

check_all_regions = ParallelAgent(
    sub_agents=[
        AgentInvocation(agent=region_health_agent, query="...us-east", output_key="us_east_health"),
        AgentInvocation(agent=region_health_agent, query="...us-west", output_key="us_west_health"),
        AgentInvocation(agent=region_health_agent, query="...eu-central", output_key="eu_central_health"),
    ],
)

synthesize_health = Agent(..., instructions="...turn the merged per-region results into one summary...")

regional_health_check = SequentialAgent(
    sub_agents=[check_all_regions, synthesize_health],
)
```

This is unchanged from `parallel-fanout-agent` - see that example's README for
why `AgentInvocation` (not three separate `AgentTool` entries) is what lets the
same agent run three times concurrently with different framing. What's
different here is what deploys, and why it has to be `regional_health_check`
rather than `check_all_regions`.

### Why the entry point can't be the bare `ParallelAgent`

```toml
# ncp.toml
[build]
entry_point = "agents.main_agent:regional_health_check"
```

A `SequentialAgent`'s last step is normally a plain `Agent`, so its text is
what the platform streams back as the answer - that's the whole mechanism
`sequential-pipeline-root-agent` and `routing-root-agent` rely on. A
`ParallelAgent` breaks that mechanism in a way neither of those workflow
shapes does: it runs several branches *concurrently*, so there is no single
place for "the terminal producer's text" to come from. Its result is
necessarily the merged dict of all branches' outputs - correct as an input to
the next step, not as a user-facing answer.

Concretely: if `ncp.toml` pointed at `check_all_regions` directly, every turn
would run the three regional checks and then have nothing to turn their
combined JSON into readable prose. `synthesize_health` is not optional
plumbing here the way a wrapping `Agent` sometimes is elsewhere - it's
what makes `ParallelAgent`'s result presentable at all, whether the pipeline
is deployed bare or wrapped in yet another `Agent`.

> **Try it:** ask this agent about fleet health. You'll see
> `check_all_regions` announced, then all three `region_health_agent`
> invocations run concurrently, then `synthesize_health` - whose summary
> streams back as the answer, exactly as it would if you deployed this same
> `regional_health_check` wrapped behind a plain `Agent` instead.

---

## 🚀 Try It Out

```bash
cd parallel-fanout-root-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy parallel-fanout-root-agent.ncp
ncp playground --agent regional_health_check --show-tools
```

### Example: Running the fan-out

**You**: How's the fleet looking?

**Agent**: runs all three regional checks concurrently, then
`synthesize_health` streams back one fleet-wide summary - the per-region JSON
never reaches the user directly.

---

## 🎓 Key Takeaways

- `ncp.toml`'s `entry_point` can name any workflow composition node, including one nested inside another - what matters is that the *outermost* node ends in a producer step
- A `ParallelAgent` (like a `DynamicParallelAgent` - see `dynamic-fanout-root-agent`) is never itself a valid deployment root; only `SequentialAgent` and `RoutingAgent` can terminate a deployment directly (see `routing-root-agent`)
- The rule generalizes: whatever you deploy as root, trace its *last-executed* step - if that step isn't a plain `Agent` producing prose, the deployment has no answer to give

## 🚀 Next Steps

- Compare with `dynamic-fanout-root-agent` and `refinement-loop-root-agent` - same shape (deploy the enclosing `SequentialAgent`, not the inner node), for a different reason each time
- Compare with `routing-root-agent`, where the inner workflow node (`RoutingAgent`) *can* be the bare root, because exactly one specialist - never several concurrently - ends up producing the answer
