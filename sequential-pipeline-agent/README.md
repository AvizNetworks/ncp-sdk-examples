# Sequential Pipeline Agent - Fixed Multi-Step Workflows with `SequentialAgent`

**Demonstrates `SequentialAgent`: a fixed, ordered pipeline of agents where each step's output feeds the next.**

---

## 🎯 What This Example Teaches

1. **`SequentialAgent`**: chaining several specialist agents into one pipeline that runs the same steps, in the same order, every time
2. **`output_key`**: naming a step's result so later steps (and the workflow itself) can refer to it
3. **Chaining vs. `share_state`**: by default a step sees only its immediate predecessor's output; `share_state=True` lets a step reach further back via `{output_key}` placeholders
4. **How a pipeline differs from an orchestrator**: `multi-agent` lets an LLM *decide* which specialist to call; a pipeline's order is decided by you, at design time

---

## 📁 Project Structure

```
sequential-pipeline-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 3 step agents + the pipeline + the entry agent
└── tools/
    ├── __init__.py
    └── postmortem_tools.py     # 🔧 get_incident, get_incident_events
```

---

## 🔗 The Pipeline: `agents/main_agent.py`

```python
from ncp import Agent, AgentTool, SequentialAgent

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

### How each step gets its input

**Chaining — the default, always on.** Each step's input is the previous step's
output text, like a Unix pipe:

```
"write a postmortem for INC-4471"
        ↓
summarize_incident  ──(its summary text)──▶  draft_timeline  ──(the timeline)──▶  draft_postmortem
```

`draft_timeline` receives the summary without either agent being configured for
it. That's the whole default model: one step, one input, no shared globals.

**`share_state=True` — opt-in, for reaching further back.** `draft_postmortem`
needs the *summary* too, and that's two steps back. With `share_state=True`,
every step's instructions get `{output_key}` placeholders filled in from all
previously recorded outputs:

```python
draft_postmortem = Agent(
    instructions="""Here is the incident summary produced earlier:

{incident_summary}

You will separately receive the incident timeline as your input.
...""",
)
```

> **Try it:** delete `share_state=True` and re-run. `{incident_summary}` is left
> in the prompt as literal text, because without it a step can only see its
> immediate predecessor. That's the difference the flag controls.

### Why the entry point is a plain `Agent`

The deployed `agent` is a normal `Agent` that exposes the pipeline as a single
tool via `AgentTool`:

```python
agent = Agent(
    name="postmortem_writer",
    tools=[AgentTool(postmortem_pipeline, name="postmortem_pipeline", description="...")],
)
```

This keeps the pipeline a *capability* rather than the agent's only behavior —
so "what can you do?" gets a direct answer instead of kicking off a three-step
drafting run.

---

## 🚀 Try It Out

```bash
cd sequential-pipeline-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy sequential-pipeline-agent.ncp
ncp playground --agent postmortem_writer --show-tools
```

### Example 1: Running the pipeline

**You**: Write a postmortem for INC-4471

**Agent**: calls `postmortem_pipeline`. You'll see each step announced as it runs
(`summarize_incident`, then `draft_timeline`), and then the finished postmortem
streams in — the last step's output is the answer. Intermediate drafts don't
appear in the final message; only the document does.

### Example 2: Not everything needs the pipeline

**You**: What can you help me with?

**Agent**: answers directly, without invoking the pipeline.

---

## 🎓 Key Takeaways

- A `SequentialAgent` runs a **fixed** sequence — use it when the steps are always the same. When the LLM should decide which specialist to call, use an `AgentTool` orchestrator instead (see `multi-agent`)
- **Chaining is automatic**; `share_state=True` is only needed when a step must reach past its immediate predecessor
- `output_key` is what makes a step's result addressable — a step without one still chains, it just can't be referenced by name
- Only the **last** step's output becomes the answer, and it streams live; earlier steps surface as progress

## 🚀 Next Steps

- Add a fourth step that drafts a customer-facing status update from `{incident_summary}`
- Swap the final step for a `LoopAgent` that revises the document until a reviewer approves it (see `refinement-loop-agent`)
- Run the first two steps concurrently instead of in sequence (see `parallel-fanout-agent`)
