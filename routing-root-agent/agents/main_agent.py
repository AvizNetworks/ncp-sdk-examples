"""Main agent definition for routing-root-agent.

Demonstrates deploying a `RoutingAgent` itself as the entry point, instead of
wrapping it as a tool behind a plain `Agent` (compare `routing-agent`, which
does the latter).

The classifier/specialists and the router are unchanged from `routing-agent`:

    request ──▶ classifier ──▶ "billing" | "technical" | "general"
                                    ↓
                        exactly one specialist answers

What's different is `ncp.toml`'s entry point:

    entry_point = "agents.main_agent:support_router"

instead of

    entry_point = "agents.main_agent:agent"

There is no wrapping `Agent` that could answer "what can you do?" directly, or
decide a message doesn't need routing at all - every message is classified and
handed to a specialist, unconditionally. That trade only makes sense when
triage-and-delegate *is* the whole product, which is exactly what a support
desk's front door is - so this is a case where the root pattern is arguably
the more natural shape, not just a leaner one.
"""

from ncp import Agent, RoutingAgent
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
# The router - this is the deployable entry point, not a plain Agent
# =============================================================================
# No wrapping Agent, no AgentTool: `ncp.toml`'s entry_point names this object
# directly, so every turn is classified and delegated unconditionally.

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
