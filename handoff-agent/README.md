# Handoff Agent - Transferring Conversations with handoff()

**Demonstrates `handoff()` (ncp-sdk >= 1.2.0): a tool-initiated transfer of the live conversation from one declared agent to another.**

---

## 🎯 What This Example Teaches

1. **`handoff()`**: how a tool tells the platform to stop the current agent and let a different, declared agent continue the same conversation
2. **`Agent.handoffs` / `max_handoffs`**: how a source agent declares which targets it may transfer to, and caps how many transfers can happen in one run
3. **How `handoff()` differs from `AgentTool`**: a handoff *transfers* the active agent and keeps the shared conversation history; `AgentTool` *delegates* a call-and-return with fresh, non-shared context (see `ncp-sdk-examples/multi-agent` for that pattern)

---

## 📁 Project Structure

```
handoff-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 triage_agent (entry) + incident_specialist (target)
└── tools/
    ├── __init__.py
    ├── triage_tools.py     # 🔧 classify_request - calls handoff()
    └── incident_tools.py   # 🔧 get_runbook, page_oncall
```

---

## 🤝 The Handoff: `agents/main_agent.py`

```python
from ncp import Agent
from tools.incident_tools import get_runbook, page_oncall
from tools.triage_tools import classify_request

incident_specialist = Agent(
    name="incident_specialist",
    description="Handles urgent network incidents...",
    instructions="...",
    tools=[get_runbook, page_oncall],
)

agent = Agent(
    name="triage_agent",
    description="Classifies network support requests...",
    instructions="...",
    tools=[classify_request],
    handoffs=[incident_specialist],   # must declare the target before handoff() can reach it
    max_handoffs=2,                   # optional cap on transfers within one run
)
```

And the tool that triggers the transfer, in `tools/triage_tools.py`:

```python
from ncp import handoff, tool

@tool
def classify_request(query: str) -> dict:
    """Classify an incoming network request and route urgent ones to the incident specialist."""
    priority = "urgent" if any(m in query.lower() for m in URGENT_MARKERS) else "normal"
    if priority == "urgent":
        handoff("incident_specialist", reason=f"urgent request: {query!r}")
    return {"query": query, "priority": priority}
```

### What actually happens on a handoff

1. `classify_request` calls `handoff("incident_specialist", ...)` - this only *schedules* the transfer; execution doesn't stop here
2. The tool returns its normal result (`{"query": ..., "priority": "urgent"}`), which is recorded in the conversation like any other tool result
3. Once the current iteration finishes, the platform stops `triage_agent`'s loop and starts `incident_specialist` **on the same conversation** - it sees everything `triage_agent` and the user said, including the just-recorded classification
4. `incident_specialist` then continues answering the user directly

`handoff()` accepts either the target `Agent` object or its name as a string (as used here) - either way, the target must already be listed in the calling agent's `handoffs=[...]`, or the call raises `RuntimeError`.

---

## 🚀 Try It Out

```bash
cd handoff-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy handoff-agent.ncp
ncp playground --agent handoff-agent --show-tools
```

### Example 1: Normal request - no handoff

**You**: How do I check which VLAN a port is assigned to?

**Agent** (`triage_agent`): classifies as `"normal"`, answers directly with general troubleshooting guidance.

### Example 2: Urgent request - triggers a handoff

**You**: Our core switch is down and the site is offline!

**Agent**: `classify_request` detects "down"/"offline", calls `handoff("incident_specialist", ...)`, and returns `{"priority": "urgent", ...}`. `triage_agent` hands off; `incident_specialist` picks up the same conversation, calls `get_runbook("link-down")`, and walks you through the escalation steps - possibly calling `page_oncall` too.

---

## 🎓 Key Takeaways

- `handoff()` is a **control-flow signal**, not a return value - call it, then return normally from the tool
- The target must be declared in `handoffs=[...]` first; `max_handoffs` bounds how many transfers can chain in one run
- Conversation history carries over across a handoff - the target agent isn't starting cold
- Choose `handoff()` for a triage → specialist pattern where the specialist should own the rest of the conversation; choose `AgentTool` (see `multi-agent`) when you just need a delegated answer folded back into the orchestrator's own response

## 🚀 Next Steps

- Add a third specialist (e.g. a security_specialist for auth/ACL issues) and extend `classify_request` to route between them
- Register `on_agent_handoff` in `AgentHooks` (see `hooks-agent`) to log every transfer as it happens
