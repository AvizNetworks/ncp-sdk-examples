"""Main agent definition for hooks-agent.

Demonstrates AgentHooks: every stage of the agent's execution loop
(agent start/complete, each iteration, each LLM call, each tool call)
fires a typed callback. This example wires up a hook for nearly every
event type and appends a one-line summary of each into a shared log
that the get_execution_log tool reads back through the chat.
"""

from ncp import Agent, AgentHooks
from tools.diagnostic_tools import check_device_health, get_execution_log, log_event


hooks = AgentHooks(
    on_agent_start=lambda data: log_event(
        f"agent_start agent={data.agent_name} max_iterations={data.max_iterations}"
    ),
    on_iteration_start=lambda data: log_event(f"iteration_start #{data.iteration}"),
    on_llm_start=lambda data: log_event(
        f"llm_start iteration={data.iteration} messages={data.message_count}"
    ),
    on_llm_complete=lambda data: log_event(
        f"llm_complete has_tool_calls={data.has_tool_calls}"
    ),
    on_token_usage=lambda data: log_event(
        f"token_usage prompt={data.prompt_tokens} completion={data.completion_tokens} "
        f"total={data.total_tokens} utilization={data.utilization_percent:.1f}%"
    ),
    on_tool_call_request=lambda data: log_event(
        f"tool_call_request tool={data.name} args={data.arguments}"
    ),
    on_tool_execution_start=lambda data: log_event(
        f"tool_execution_start tool={data.name}"
    ),
    on_tool_execution_complete=lambda data: log_event(
        f"tool_execution_complete tool={data.name} result={data.result}"
    ),
    on_tool_execution_error=lambda data: log_event(
        f"tool_execution_error tool={data.name} error={data.error}"
    ),
    on_iteration_complete=lambda data: log_event(
        f"iteration_complete #{data.iteration} tool_calls_executed={data.tool_calls_executed}"
    ),
    on_agent_complete=lambda data: log_event(
        f"agent_complete total_iterations={data.total_iterations}"
    ),
    on_agent_error=lambda data: log_event(
        f"agent_error iteration={data.iteration} error={data.error}"
    ),
)


agent = Agent(
    name="HooksAgent",
    description="A network diagnostics agent that demonstrates AgentHooks observing its own execution",
    instructions="""You are a network diagnostics assistant.

You have two tools:
- check_device_health(hostname): checks a device's health. Hostnames containing
  "down", "offline", or "unreachable" simulate an unreachable device and will error.
- get_execution_log(clear=False): returns the log of execution events this
  agent's hooks have captured so far (agent start/complete, each LLM call,
  each tool call).

When asked to check a device, call check_device_health. If asked to check
several devices, call it once per device. When asked to show the execution
log, hook log, or "what happened", call get_execution_log and present the
entries as a readable list, in order. If a health check fails, report the
error plainly - don't hide it.""",
    tools=[check_device_health, get_execution_log],
    hooks=hooks,
)
