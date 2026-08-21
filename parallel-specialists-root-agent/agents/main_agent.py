"""Main agent definition for parallel-specialists-root-agent.

Demonstrates `ParallelAgent` fanning out to *different* specialist agents
(instead of `parallel-fanout-root-agent`'s one specialist invoked three times
via `AgentInvocation`), still deployed via its enclosing `SequentialAgent` as
the entry point.

Three independent specialists check one device concurrently, each looking at
a different axis of risk:

    run_all_audits (ParallelAgent) ─┬─▶ firmware_auditor ──┐
                                    ├─▶ exposure_auditor  ──┼─▶ merged results
                                    └─▶ auth_auditor      ──┘
                                              ↓
                                   synthesize_device_risk  (the answer)

**Why no `AgentInvocation` this time.** `parallel-fanout-agent` needed
`AgentInvocation` because the *same* `region_health_agent` object had to run
three times with three different queries, and an agent's tools (including
`AgentTool`-wrapped sub-agents) can't repeat a name - `AgentInvocation` lives
in `sub_agents` instead, which has no such uniqueness constraint. Here there
is no repetition: `firmware_auditor`, `exposure_auditor`, and `auth_auditor`
are three distinct agents with three distinct names, so they go straight into
`ParallelAgent.sub_agents` as themselves. Each already carries its own
`output_key`, and - since no entry overrides the query - each receives the
same input: whatever device name the user asked about.

**Why this still isn't the bare `ParallelAgent`.** The reasoning is identical
to `parallel-fanout-root-agent`: three branches run concurrently, so there is
no single terminal producer, and `run_all_audits`'s own result is a merged
dict, not prose. `synthesize_device_risk` is what turns three specialists'
independent findings into one answer - which is why the entry point is
`device_risk_check` (the `SequentialAgent` that wraps the fan-out with that
synthesis step), not `run_all_audits` on its own.
"""

from ncp import Agent, ParallelAgent, SequentialAgent
from tools.device_tools import get_auth_config, get_firmware_status, get_open_ports


# =============================================================================
# Three distinct specialists - each looks at one axis of device risk
# =============================================================================

firmware_auditor = Agent(
    name="firmware_auditor",
    description="Checks a device's firmware version and end-of-life status",
    instructions="""You check firmware risk for one device.

Your input names the device to check. Call get_firmware_status with it, then
report the firmware version and whether it is end-of-life (EOL). If it is
EOL, say how long it has been.

Finish with a one-word verdict on its own line: OK or EOL.""",
    tools=[get_firmware_status],
    output_key="firmware_findings",
)

exposure_auditor = Agent(
    name="exposure_auditor",
    description="Checks a device's open ports and exposed services",
    instructions="""You check exposure risk for one device.

Your input names the device to check. Call get_open_ports with it, then list
the open ports and exposed services. Flag any of these as risky if present:
telnet, http-admin (unencrypted admin access), or snmp-v1.

Finish with a one-word verdict on its own line: OK or EXPOSED.""",
    tools=[get_open_ports],
    output_key="exposure_findings",
)

auth_auditor = Agent(
    name="auth_auditor",
    description="Checks a device's authentication configuration",
    instructions="""You check authentication risk for one device.

Your input names the device to check. Call get_auth_config with it, then
report the auth method and whether MFA is enabled. Flag default credentials
as a critical finding if present.

Finish with a one-word verdict on its own line: OK or WEAK.""",
    tools=[get_auth_config],
    output_key="auth_findings",
)


# =============================================================================
# Fan-out: three different agents, each already uniquely named - no
# AgentInvocation needed, unlike parallel-fanout-agent's repeated-agent case.
# =============================================================================

run_all_audits = ParallelAgent(
    name="run_all_audits",
    description="Runs firmware, exposure, and auth checks concurrently against one device",
    sub_agents=[firmware_auditor, exposure_auditor, auth_auditor],
)


# =============================================================================
# Gather: turn the three independent findings into one risk report
# =============================================================================
# A ParallelAgent's own output is a merged {output_key: text} mapping, not
# prose - so it feeds this synthesizer rather than answering the user itself.
# This step is what lets device_risk_check be deployed as root at all: it is
# the pipeline's last step, so ITS text is what streams to the user.

synthesize_device_risk = Agent(
    name="synthesize_device_risk",
    description="Turns three independent per-device findings into one risk report",
    instructions="""You write device security risk reports.

Your input is a JSON object mapping firmware_findings, exposure_findings, and
auth_findings to that specialist's report.

Write a short report that:
1. Opens with an overall verdict: CLEAN (all three OK), AT-RISK (one flagged),
   or CRITICAL (default credentials, or two or more flagged)
2. Gives one line per axis (firmware, exposure, auth) with its verdict and the
   single most important fact
3. Ends with "Fix first:" and the single highest-priority remediation, or
   says there is nothing to fix if everything is CLEAN.""",
)


# =============================================================================
# The pipeline - this is the deployable entry point, not a plain Agent
# =============================================================================
# No wrapping Agent, no AgentTool: `ncp.toml`'s entry_point names this object
# directly. run_all_audits itself is never the entry point - see the module
# docstring, and parallel-fanout-root-agent's, for why a bare ParallelAgent
# can't be one.

device_risk_check = SequentialAgent(
    name="device_risk_check",
    description="Checks a device's firmware, exposure, and auth risk concurrently, then reports",
    sub_agents=[run_all_audits, synthesize_device_risk],
)
