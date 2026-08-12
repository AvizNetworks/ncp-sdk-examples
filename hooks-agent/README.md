# Hooks Agent - Observing Agent Execution with AgentHooks

**Demonstrates `AgentHooks` (ncp-sdk >= 1.2.0): typed callbacks that observe every stage of an agent's run without affecting it.**

---

## 🎯 What This Example Teaches

1. **AgentHooks**: registering a callback for each stage of the execution loop (agent start/complete, each iteration, each LLM call, each tool call)
2. **Typed event payloads**: every hook receives a dataclass specific to that event (`AgentStartData`, `ToolExecutionCompleteData`, ...)
3. **Hooks are observation-only**: they can't change what the agent does, can raise without breaking the run (exceptions are logged and swallowed), and may be sync or `async def`
4. **A pattern for making hook activity visible in chat**: since hook output doesn't otherwise reach `ncp playground`, this example has its hooks append to a shared log that a tool reads back

---

## 📁 Project Structure

```
hooks-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py          # 🎯 Agent + AgentHooks wiring
└── tools/
    ├── __init__.py
    └── diagnostic_tools.py    # 🔧 check_device_health, get_execution_log, shared log
```

---

## 🪝 The Hooks: `agents/main_agent.py`

```python
from ncp import Agent, AgentHooks
from tools.diagnostic_tools import check_device_health, get_execution_log, log_event

hooks = AgentHooks(
    on_agent_start=lambda data: log_event(f"agent_start agent={data.agent_name} ..."),
    on_tool_execution_start=lambda data: log_event(f"tool_execution_start tool={data.name}"),
    on_tool_execution_complete=lambda data: log_event(f"tool_execution_complete tool={data.name} ..."),
    on_tool_execution_error=lambda data: log_event(f"tool_execution_error tool={data.name} ..."),
    on_agent_complete=lambda data: log_event(f"agent_complete total_iterations={data.total_iterations}"),
    # ...plus on_iteration_start, on_llm_start, on_llm_complete, on_token_usage,
    #    on_tool_call_request, on_iteration_complete, on_agent_error
)

agent = Agent(
    name="HooksAgent",
    description="...",
    instructions="...",
    tools=[check_device_health, get_execution_log],
    hooks=hooks,
)
```

`AgentHooks` has one optional field per lifecycle event - leave any of them `None` and that event is simply not observed. Every field takes a plain function or `async def`; the executor calls whichever is provided and moves on regardless of what it does.

### Why the hooks call `log_event()` instead of `print()`

Hooks run wherever the agent executes (on the NCP platform once deployed). Their `print()`/logging output lands in the platform's own process, not in your `ncp playground` terminal. So this example's hooks each append one line to an in-memory list (`tools/diagnostic_tools.py::execution_log`), and the `get_execution_log` tool hands that list back to you as a normal tool result — which *is* visible in the chat. This is the reusable pattern for any hook-based example you build: log to shared state, expose it through a tool.

## 🔧 The Tools: `tools/diagnostic_tools.py`

- **`check_device_health(hostname)`** — simulates a device health check. Hostnames containing `"down"`, `"offline"`, or `"unreachable"` raise a `ConnectionError`, so you can trigger `on_tool_execution_error` on demand.
- **`get_execution_log(clear=False)`** — returns everything the hooks have logged so far, oldest first.

---

## 🚀 Try It Out

```bash
cd hooks-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy hooks-agent.ncp
ncp playground --agent hooks-agent --show-tools --logs DEBUG
```

### Example 1: Watch the full lifecycle

**You**: Check the health of switch-core-1, then show me the execution log

**Agent**: calls `check_device_health("switch-core-1")`, then `get_execution_log()`, and reports back something like:

```
[14:02:01] agent_start agent=HooksAgent max_iterations=25
[14:02:01] iteration_start #1
[14:02:01] llm_start iteration=1 messages=2
[14:02:02] llm_complete has_tool_calls=True
[14:02:02] tool_call_request tool=check_device_health args={'hostname': 'switch-core-1'}
[14:02:02] tool_execution_start tool=check_device_health
[14:02:02] tool_execution_complete tool=check_device_health result={'hostname': 'switch-core-1', 'status': 'healthy', ...}
[14:02:02] iteration_complete #1 tool_calls_executed=1
...
[14:02:03] agent_complete total_iterations=2
```

### Example 2: Trigger the error hook

**You**: Check the health of router-offline-3

**Agent**: `check_device_health` raises `ConnectionError`, `on_tool_execution_error` fires and logs it, and the agent reports the failure instead of a health result. Ask for the execution log afterward to see the `tool_execution_error` line.

---

## 🎓 Key Takeaways

- `AgentHooks` fields map 1:1 to `ExecutionEventType` stages - register only the ones you need
- Each hook gets a typed payload (see `ncp.AgentStartData`, `ncp.ToolExecutionCompleteData`, etc. in the SDK) - no need to parse a generic dict
- Hooks never break the run: a hook that raises just gets logged and skipped
- Hooks are the right tool for cross-cutting concerns - metrics, audit trails, custom logging - that shouldn't live inside every tool

## 🚀 Next Steps

- Add `on_agent_handoff` and pair this example with `handoff-agent` to see a hook fire when control transfers between agents
- Add `on_status_update` / `on_tool_stream` and pair with `streaming-status-agent` to observe `send_status()` / `send_content()` calls from the outside
