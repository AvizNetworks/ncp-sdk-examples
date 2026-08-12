"""Main agent definition for handoff-agent.

Demonstrates handoff(): a triage agent classifies incoming requests and,
for anything urgent, transfers the live conversation to a specialist
incident-response agent. The specialist then answers the user directly,
continuing the same conversation history - unlike AgentTool, which nests a
call-and-return with fresh, non-shared context.
"""

from ncp import Agent
from tools.incident_tools import get_runbook, page_oncall
from tools.triage_tools import classify_request


incident_specialist = Agent(
    name="incident_specialist",
    description="Handles urgent network incidents: outages, flapping links, unreachable devices",
    instructions="""You are a network incident-response specialist. A triage agent has just
handed this conversation to you because the request looked urgent.

You have two tools:
- get_runbook(incident_type): look up response steps for a known incident type
  ("link-down", "bgp-flap"; anything else returns a generic escalation runbook)
- page_oncall(reason): page the on-call network engineer

Workflow:
1. Identify the incident type from the user's request
2. Call get_runbook to retrieve the steps
3. Walk the user through the steps
4. If the runbook says to escalate, or the user asks you to, call page_oncall

Be calm, direct, and action-oriented - this is an active incident.""",
    tools=[get_runbook, page_oncall],
)

agent = Agent(
    name="triage_agent",
    description="Classifies network support requests and hands off urgent ones to an incident specialist",
    instructions="""You are the first point of contact for network support requests.

Call classify_request with the user's request, verbatim, to determine its
priority. If it comes back "urgent", a handoff to the incident specialist has
already been triggered - just briefly acknowledge that you're transferring
them and stop; the specialist will continue the conversation from here. If it
comes back "normal", handle the request yourself with general network
troubleshooting advice.""",
    tools=[classify_request],
    handoffs=[incident_specialist],
    max_handoffs=2,
)
