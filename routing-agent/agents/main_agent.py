"""Main agent definition for routing-agent.

Demonstrates RoutingAgent: classify the request once, up front, then hand the
whole thing to exactly one specialist.

    request ──▶ classifier ──▶ "billing" | "technical" | "general"
                                    ↓
                        exactly one specialist answers

This is the simplest of the three "pick a specialist" patterns in this repo, and
the differences between them matter:

- **RoutingAgent (here)** classifies **once, before any specialist starts**, then
  fully delegates. The router itself never talks to the user - its output is a
  route label, not an answer. One decision, one specialist, done.

- **`handoff-agent`** (`Agent.handoffs` + `handoff()`) transfers a conversation
  that is **already underway**. The first agent starts answering, decides
  mid-flight that this belongs to someone else, and passes the live conversation
  over - shared history and all.

- **`multi-agent`** (`AgentTool` orchestrator) keeps a parent agent **in control
  the whole time**. It calls specialists as tools, possibly several of them,
  possibly repeatedly, and writes the final answer itself.

Rule of thumb: routing is for triage where one specialist owns the answer,
handoff is for escalation mid-conversation, and an orchestrator is for work that
needs composing from several specialists.
"""

from ncp import Agent, AgentTool, RoutingAgent
from tools.support_tools import look_up_invoice, search_kb


# =============================================================================
# The classifier - emits a route label, never an answer
# =============================================================================

classifier = Agent(
    name="classifier",
    description="Classifies a support request into exactly one category",
    instructions="""You classify incoming support requests. You do not answer them.

Read the request and reply with EXACTLY ONE of these words, lowercase, with no
punctuation, explanation, or extra text:

billing    - invoices, payments, refunds, pricing, contracts, renewals
technical  - connectivity, VPN, wifi, latency, outages, device problems
general    - anything else: hours, contacts, account changes, how-to questions

Correct reply: billing
Wrong reply:   This looks like a billing question.""",
)


# =============================================================================
# The specialists - exactly one of these will run
# =============================================================================

billing_agent = Agent(
    name="billing_agent",
    description="Handles invoice, payment, and pricing questions",
    instructions="""You handle billing questions for a network services provider.

If the user mentions an invoice ID (e.g. ACME-2291), call look_up_invoice and
give them its amount and status. Flag anything overdue clearly and say how many
days it has been outstanding.

If they ask about pricing or contracts generally, answer helpfully and offer to
connect them with their account manager. Be precise about money - never estimate
or round an amount you looked up.""",
    tools=[look_up_invoice],
)

technical_agent = Agent(
    name="technical_agent",
    description="Handles connectivity and device troubleshooting",
    instructions="""You are a network support engineer.

Identify the technical topic (vpn, wifi, latency, ...) and call search_kb with
it. Walk the user through the returned steps in order, in plain language,
explaining what each step is checking for and what result would confirm the
problem.

If the knowledge base has no article, say so directly and ask the two or three
diagnostic questions that would most narrow it down.""",
    tools=[search_kb],
)

general_agent = Agent(
    name="general_agent",
    description="Handles general enquiries that aren't billing or technical",
    instructions="""You handle general support enquiries.

Answer helpfully and concisely. If the request turns out to be a billing or
technical matter after all, say which team handles it and what detail they'll
need (an invoice ID, or the affected site and time window).""",
)


# =============================================================================
# The router
# =============================================================================

support_router = RoutingAgent(
    name="support_router",
    description="Routes a support request to the billing, technical, or general specialist",
    router=classifier,
    routes={
        "billing": billing_agent,
        "technical": technical_agent,
        "general": general_agent,
    },
    # If the classifier returns something unexpected, fall back rather than
    # failing the request. Without a default, an unmatched label is an error.
    default_route="general",
)


# =============================================================================
# The deployable agent
# =============================================================================

agent = Agent(
    name="support_desk",
    description="Support desk that routes each request to the right specialist",
    instructions="""You are the front door of a network services support desk.

For any actual support request - billing, technical, or general - call
support_router with the user's message verbatim. It classifies the request and
routes it to the right specialist, then returns their answer. Present that
answer to the user as the response.

Only handle a message yourself if it is small talk or a direct question about
what you can do.""",
    tools=[
        AgentTool(
            support_router,
            name="support_router",
            description=(
                "Route a support request to the correct specialist and return "
                "their answer. Pass the user's message verbatim."
            ),
        )
    ],
)
