# Routing Root Agent - Deploying a `RoutingAgent` as the Entry Point

**Demonstrates deploying a `RoutingAgent` itself as the entry point, instead of wrapping it as a tool behind a plain `Agent`.**

---

## 🎯 What This Example Teaches

1. **A `RoutingAgent` can be the entry point, same as `SequentialAgent`.** `ncp.toml`'s `entry_point` names `support_router` directly - the platform's `WorkflowExecutor` runs it through the same `execute(messages, user_message)` shape `AgentExecutor` uses for a plain `Agent` (see `sequential-pipeline-root-agent` for the general mechanism).
2. **Why this shape fits routing especially well.** Unlike a drafting pipeline, a triage front door has no other job - "classify, then delegate" *is* the whole product. Skipping the wrapping `Agent` costs you almost nothing here.
3. **What you still give up.** There's no step that can answer "what can you do?" without running the classifier - every message gets classified and routed, even small talk.

---

## 📁 Project Structure

```
routing-root-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 classifier + 3 specialists + the router - no wrapping Agent
└── tools/
    ├── __init__.py
    └── support_tools.py         # 🔧 look_up_invoice, search_kb
```

---

## 🔗 The Router: `agents/main_agent.py`

```python
from ncp import Agent, RoutingAgent

classifier      = Agent(..., instructions="reply with exactly one of: billing, technical, general")
billing_agent   = Agent(..., tools=[look_up_invoice])
technical_agent = Agent(..., tools=[search_kb])
general_agent   = Agent(...)

support_router = RoutingAgent(
    name="support_router",
    router=classifier,
    routes={"billing": billing_agent, "technical": technical_agent, "general": general_agent},
    default_route="general",
)
```

The classifier and specialists are identical to `routing-agent` - see that
example's README for how `RoutingAgent` classifies once and fully delegates
(as opposed to `handoff-agent`'s mid-conversation transfer or `multi-agent`'s
orchestrator that stays in control). What's different here is what deploys.

### The entry point *is* the router

```toml
# ncp.toml
[build]
entry_point = "agents.main_agent:support_router"
```

There is no `agent = Agent(tools=[AgentTool(support_router, ...)])` step.
`support_router` - a `RoutingAgent`, not an `Agent` - is deployed directly.
Every incoming message goes straight into the classifier, and whichever
specialist it names produces the answer.

### Why routing tolerates this better than a pipeline does

`sequential-pipeline-root-agent` called out a real cost of skipping the
wrapping `Agent`: no triage, so an off-pipeline message like "what can you do?"
gets fed into the pipeline anyway. The same cost exists here in principle, but
it matters less in practice:

- A postmortem pipeline is one capability that a broader agent might also need
  to *not* run.
- A support desk's classifier is *already* a triage step - "general" is a
  legitimate route for exactly the small-talk / capability questions a
  wrapping `Agent` would otherwise intercept.

> **Try it:** ask "what can you do?" The classifier will most likely call it
> `general`, and `general_agent` gives a reasonable answer anyway - because
> "general" was designed to catch what the classifier can't confidently place
> as billing or technical. That's not true of every workflow: it's specific to
> routing already having a catch-all route.

---

## 🚀 Try It Out

```bash
cd routing-root-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy routing-root-agent.ncp
ncp playground --agent support_router --show-tools
```

### Example: Routing a request

**You**: My invoice ACME-2291 looks overdue, can you check?

**Agent**: the classifier reads `billing`, `billing_agent` calls
`look_up_invoice`, and its answer streams back as the response - the
classification step itself never appears in the final message.

---

## 🎓 Key Takeaways

- A `RoutingAgent` can be `ncp.toml`'s entry point directly, exactly like a `SequentialAgent` can
- Routing is one of the workflow shapes where skipping the wrapping `Agent` costs the least, because the router's `default_route` already functions as a catch-all
- Compare directly against `routing-agent` - same classifier, same specialists, only the entry point differs

## 🚀 Next Steps

- Compare with `sequential-pipeline-root-agent`, where skipping the wrapping `Agent` has a sharper cost (there's no catch-all route to fall back on)
- Try removing `default_route` and see the router raise instead of silently guessing, when the classifier's output doesn't match any route label
