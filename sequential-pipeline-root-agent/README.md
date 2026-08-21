# Sequential Pipeline Root Agent - Deploying a `SequentialAgent` as the Entry Point

**Demonstrates deploying a `SequentialAgent` itself as the entry point, instead of wrapping it as a tool behind a plain `Agent`.**

---

## 🎯 What This Example Teaches

1. **A workflow node can be the entry point.** `ncp.toml`'s `entry_point` doesn't have to name a plain `Agent` - it can name a `SequentialAgent`/`ParallelAgent`/`LoopAgent`/etc. directly, because the platform's `WorkflowExecutor` runs a workflow node through the exact same `execute(messages, user_message)` shape `AgentExecutor` uses for a plain `Agent`.
2. **What that trades away.** With a plain `Agent` as root (see `sequential-pipeline-agent`), an LLM triages first and only invokes the pipeline when the request warrants it. With the pipeline itself as root, there is no triage - every message is step 1's input, unconditionally.
3. **When each shape is the right call.** Pipeline-as-root fits a single-purpose deployment where the pipeline *is* the whole product. Wrapping in a plain `Agent` fits a deployment that also needs to answer other questions, or offers the pipeline as one capability among several.

---

## 📁 Project Structure

```
sequential-pipeline-root-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 3 step agents + the pipeline - no wrapping Agent
└── tools/
    ├── __init__.py
    └── postmortem_tools.py     # 🔧 get_incident, get_incident_events
```

---

## 🔗 The Pipeline: `agents/main_agent.py`

```python
from ncp import Agent, SequentialAgent

summarize_incident = Agent(..., tools=[get_incident],        output_key="incident_summary")
draft_timeline     = Agent(..., tools=[get_incident_events], output_key="timeline")
draft_postmortem   = Agent(..., instructions="...{incident_summary}...")

postmortem_pipeline = SequentialAgent(
    name="postmortem_pipeline",
    description="Summarizes an incident, builds its timeline, then writes the postmortem",
    sub_agents=[summarize_incident, draft_timeline, draft_postmortem],
    share_state=True,
)
```

The three steps and their chaining/`share_state` behavior are identical to
`sequential-pipeline-agent` - see that example's README for how chaining and
`{output_key}` templating work. What's different here is what happens next.

### The entry point *is* the pipeline

```toml
# ncp.toml
[build]
entry_point = "agents.main_agent:postmortem_pipeline"
```

There is no `agent = Agent(tools=[AgentTool(postmortem_pipeline, ...)])` step.
`postmortem_pipeline` - a `SequentialAgent`, not an `Agent` - is deployed
directly. Every incoming message becomes `summarize_incident`'s input, and
the pipeline always runs all three steps.

### The tradeoff this makes

| | Plain `Agent` root (`sequential-pipeline-agent`) | `SequentialAgent` root (this example) |
|---|---|---|
| "What can you do?" | Answered directly, no pipeline run | Fed into `summarize_incident` as if it were an incident ID - it will fail to find a matching record |
| Every real request | LLM decides to call the pipeline tool | Pipeline runs unconditionally |
| Right for | An agent with other capabilities, or that should gate expensive pipeline runs | A deployment whose *only* job is running this pipeline |

> **Try it:** ask this agent something unrelated to an incident, like "what can
> you do?" There's no triage step to catch it - `summarize_incident` calls
> `get_incident` with whatever it was given and reports it can't find a
> matching record. That's the cost of skipping the wrapping `Agent`.

---

## 🚀 Try It Out

```bash
cd sequential-pipeline-root-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy sequential-pipeline-root-agent.ncp
ncp playground --agent postmortem_pipeline --show-tools
```

### Example: Running the pipeline

**You**: INC-4471

**Agent**: runs all three steps unconditionally - you'll see each step
announced as it runs (`summarize_incident`, then `draft_timeline`), and then
the finished postmortem streams in as the answer.

---

## 🎓 Key Takeaways

- `ncp.toml`'s `entry_point` can name any workflow composition node, not just a plain `Agent` - the platform runs both through the same executor interface
- Deploying the pipeline as root means no triage: every message runs the full pipeline, with no way to answer an off-pipeline question directly
- Use this shape only when the pipeline is the deployment's entire purpose; otherwise wrap it behind a plain `Agent` (see `sequential-pipeline-agent`) so it stays a capability rather than the only behavior

## 🚀 Next Steps

- Compare this directly against `sequential-pipeline-agent` - same pipeline, same tools, only the entry point differs
- Try a `RoutingAgent` as root instead, so a one-shot classifier can send an off-pipeline request somewhere else without a full orchestrator LLM (see `routing-agent`)
