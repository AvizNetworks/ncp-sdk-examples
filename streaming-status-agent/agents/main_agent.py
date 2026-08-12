"""Main agent definition for streaming-status-agent.

Demonstrates send_status() and send_content(): a long-running tool reports
overall progress via send_status() (replace-in-place) and streams partial
results via send_content() (append-only), while AgentHooks observes both
from the outside via on_status_update / on_tool_stream.
"""

from ncp import Agent, AgentHooks
from tools.backup_tools import backup_devices, get_stream_log, log_stream_event

hooks = AgentHooks(
    on_status_update=lambda data: log_stream_event(
        f"status_update type={data.status_type} message={data.status_message!r}"
    ),
    on_tool_stream=lambda data: log_stream_event(
        f"tool_stream tool={data.tool_name} chunk={data.chunk!r}"
    ),
)

agent = Agent(
    name="StreamingStatusAgent",
    description="Backs up network device configs, reporting progress and partial results as it works",
    instructions="""You are a network operations assistant.

You have two tools:
- backup_devices(hostnames): backs up configs for a list of device hostnames,
  reporting progress and per-device results as it goes
- get_stream_log(clear=False): returns the log of status/streaming events
  this agent's hooks have captured so far

When asked to back up one or more devices, call backup_devices with the full
list in a single call - don't call it once per device. When asked to show
the stream log or "what was streamed", call get_stream_log and present the
entries as a readable list, in order.""",
    tools=[backup_devices, get_stream_log],
    hooks=hooks,
)
