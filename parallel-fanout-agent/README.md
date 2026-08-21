# Parallel Fan-Out Agent - Concurrent Work with `ParallelAgent`

**Demonstrates `ParallelAgent` + `AgentInvocation`: running the same specialist agent several times concurrently, each on a different task, then gathering the results.**

---

## 🎯 What This Example Teaches

1. **`ParallelAgent`**: running branches concurrently instead of one after another
2. **`AgentInvocation`**: reusing one agent object in several slots, each with its own input (`query`) and result name (`output_key`)
3. **Fan-out/gather**: a `ParallelAgent` produces a merged mapping, so it's normally followed by a synthesizer step inside a `SequentialAgent`
4. **Why `AgentTool` can't do this**: tool names must be unique, so the same agent can't appear three times in one `tools` list

---

## 📁 Project Structure

```
parallel-fanout-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py        # 🎯 1 specialist, 3 invocations, + synthesizer
└── tools/
    ├── __init__.py
    └── region_tools.py      # 🔧 get_region_health, list_regions
```

---

## 🔀 The Fan-Out: `agents/main_agent.py`

One specialist, defined **once**:

```python
region_health_agent = Agent(
    name="region_health_agent",
    description="Assesses the health of a single network region",
    instructions="...Finish with a one-word verdict: HEALTHY, DEGRADED, or CRITICAL.",
    tools=[get_region_health],
)
```

…invoked **three times, concurrently**, each with different framing:

```python
check_all_regions = ParallelAgent(
    name="check_all_regions",
    description="Checks every region's health concurrently",
    sub_agents=[
        AgentInvocation(agent=region_health_agent,
                        query="Assess the health of region: us-east",
                        output_key="us_east_health"),
        AgentInvocation(agent=region_health_agent,
                        query="Assess the health of region: us-west",
                        output_key="us_west_health"),
        AgentInvocation(agent=region_health_agent,
                        query="Assess the health of region: eu-central",
                        output_key="eu_central_health"),
    ],
)
```

```
                 ┌─▶ region_health_agent("us-east")    ─┐
ParallelAgent  ──┼─▶ region_health_agent("us-west")    ─┼─▶ merged results
                 └─▶ region_health_agent("eu-central") ─┘
                                    ↓
                            synthesize_health
```

### Why `AgentInvocation` exists

An agent's tools must have **unique names**, and that includes `AgentTool`-wrapped
sub-agents — otherwise only one of them would be reachable by the LLM, and the
rest would silently disappear. So this doesn't work:

```python
# ✗ Three tools, one name — rejected
Agent(tools=[AgentTool(region_health_agent),
             AgentTool(region_health_agent),
             AgentTool(region_health_agent)])
```

`AgentInvocation` sidesteps it entirely by living in `sub_agents` rather than
`tools`, where no such uniqueness constraint applies. It wraps a node to override
just that one slot's input and result name.

### Gathering the results

A `ParallelAgent`'s own output is a merged `{output_key: text}` mapping — useful
structured data, but not a user-facing answer. So it's wrapped in a
`SequentialAgent` with a synthesizer step that turns the three reports into one:

```python
regional_health_check = SequentialAgent(
    name="regional_health_check",
    sub_agents=[check_all_regions, synthesize_health],
)
```

The synthesizer is the pipeline's last step, so **its** answer is what streams
back to the user.

---

## 🚀 Try It Out

```bash
cd parallel-fanout-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy parallel-fanout-agent.ncp
ncp playground --agent fleet_health_monitor --show-tools
```

### Example 1: Full fan-out

**You**: How's the fleet looking today?

**Agent**: calls `regional_health_check`. All three regions are assessed at the
same time rather than one after another, then the synthesizer reports the
fleet verdict — flagging `eu-central` (CRITICAL, sustained CRC errors) and
`us-east` (DEGRADED, 2 devices down).

### Example 2: No fan-out needed

**You**: Which regions do you monitor?

**Agent**: calls `list_regions` and answers directly — no reason to spin up three
concurrent branches for that.

---

## 🎓 Key Takeaways

- `ParallelAgent` runs branches **concurrently** — use it when the branches don't depend on each other
- Every branch receives the same input by default; `AgentInvocation(query=...)` overrides it per-slot
- `AgentInvocation(output_key=...)` is what keeps three runs of one agent from overwriting each other's results
- A `ParallelAgent` produces a merged mapping, so **pair it with a synthesizer step** to get prose

## 🚀 Next Steps

- Add a fourth region and watch the branch count grow without touching the specialist
- Let a planner decide which regions to check at runtime (see `dynamic-fanout-agent`)
- Cap how many branches run at once with `DynamicParallelAgent(max_concurrency=...)`
