# Parallel Specialists Root Agent - `ParallelAgent` Fanning Out to Different Sub-Agents

**Demonstrates `ParallelAgent` fanning out to *different* specialist agents rather than the same agent invoked several times - still deployed via its enclosing `SequentialAgent` as the entry point.**

---

## 🎯 What This Example Teaches

1. **`ParallelAgent.sub_agents` with distinct agents needs no `AgentInvocation`.** `parallel-fanout-root-agent` needed `AgentInvocation` to run *one* agent three times with three different queries. Here there are three different agents, each already uniquely named, so they go straight into `sub_agents` as themselves.
2. **The root rule is unchanged.** A bare `ParallelAgent` still can't be the entry point, for the same reason as `parallel-fanout-root-agent`: three branches run concurrently, so there's no single terminal producer, and the result is a merged dict, not prose. The entry point is `device_risk_check` (the `SequentialAgent` wrapping the fan-out with a synthesizer), not `run_all_audits` on its own.
3. **When to reach for which shape.** Same specialist, several framings → `AgentInvocation` (`parallel-fanout-root-agent`). Several different specialists, one shared input → plain `ParallelAgent.sub_agents` (this example).

---

## 📁 Project Structure

```
parallel-specialists-root-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 3 distinct specialists + fan-out + synthesizer - no wrapping Agent
└── tools/
    ├── __init__.py
    └── device_tools.py          # 🔧 get_firmware_status, get_open_ports, get_auth_config
```

---

## 🔗 The Pipeline: `agents/main_agent.py`

```python
from ncp import Agent, ParallelAgent, SequentialAgent

firmware_auditor  = Agent(..., tools=[get_firmware_status], output_key="firmware_findings")
exposure_auditor  = Agent(..., tools=[get_open_ports],       output_key="exposure_findings")
auth_auditor      = Agent(..., tools=[get_auth_config],      output_key="auth_findings")

run_all_audits = ParallelAgent(
    name="run_all_audits",
    sub_agents=[firmware_auditor, exposure_auditor, auth_auditor],
)

synthesize_device_risk = Agent(..., instructions="...turn three findings into one risk report...")

device_risk_check = SequentialAgent(
    sub_agents=[run_all_audits, synthesize_device_risk],
)
```

Each of the three specialists is already a distinct `Agent` with its own name
and `output_key`, so `run_all_audits.sub_agents` lists them directly - no
`AgentInvocation` wrapper is needed anywhere here. Compare with
`parallel-fanout-root-agent`, where `region_health_agent` is the *same*
object listed three times, each wrapped in an `AgentInvocation` to give it a
different query and a different `output_key` (an agent's tools, including
`AgentTool`-wrapped sub-agents, can't repeat a name - `AgentInvocation`
sidesteps that by living in `sub_agents` instead).

Since none of the three entries override the query, `ParallelAgent`'s default
fan-out rule applies as-is: every branch receives the *same* input - whatever
device name is in the user's message.

### Why the entry point still can't be the bare `ParallelAgent`

```toml
# ncp.toml
[build]
entry_point = "agents.main_agent:device_risk_check"
```

Using different sub-agents doesn't change the constraint `parallel-fanout-
root-agent` documents: three branches still run concurrently, so there is
still no single terminal producer, and `run_all_audits`'s own output is still
a merged `{output_key: text}` dict, not prose. `synthesize_device_risk` is
what makes the three specialists' independent findings presentable as one
answer - exactly as true here as it is when the branches all share one
underlying agent.

> **Try it:** ask this agent to check `access-sw-03`. You'll see
> `run_all_audits` announced, then all three specialists run concurrently
> (each against the same device name), then `synthesize_device_risk` streams
> back one report - likely CRITICAL, since that device has both default
> credentials and EOL firmware.

---

## 🚀 Try It Out

```bash
cd parallel-specialists-root-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy parallel-specialists-root-agent.ncp
ncp playground --agent device_risk_check --show-tools
```

### Example: Checking a device

**You**: Check core-sw-01 for security risk

**Agent**: `firmware_auditor`, `exposure_auditor`, and `auth_auditor` run
concurrently against `core-sw-01`; `synthesize_device_risk` streams back a
report opening with AT-RISK (EOL firmware and an exposed telnet/http-admin
surface, but no default credentials).

### Example: A clean device

**You**: Check edge-fw-02

**Agent**: same three specialists, same synthesis step - this time the
report opens with CLEAN, since `edge-fw-02` has current firmware, no risky
exposed services, and MFA enabled.

---

## 🎓 Key Takeaways

- `ParallelAgent.sub_agents` can list distinct agents directly; `AgentInvocation` is only needed to run the *same* agent more than once with different framing (see `parallel-fanout-root-agent`)
- The "can't be a bare root" rule for `ParallelAgent` applies regardless of whether its branches are the same agent repeated or different specialists - what matters is concurrency, not repetition
- Every branch shares one input unless an entry explicitly overrides it with `AgentInvocation(query=...)`

## 🚀 Next Steps

- Compare directly against `parallel-fanout-root-agent` - same root shape, opposite reason for needing (or not needing) `AgentInvocation`
- Add a fourth specialist (e.g. a config-drift check) - since there's no repeated agent here, it's just one more entry in `sub_agents`, no `AgentInvocation` bookkeeping required
