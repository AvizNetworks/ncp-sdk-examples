"""Main agent definition for sequential-pipeline-root-agent.

Demonstrates deploying a `SequentialAgent` itself as the entry point, instead
of wrapping it as a tool behind a plain `Agent` (compare `sequential-pipeline-
agent`, which does the latter).

The platform's `WorkflowExecutor` runs a workflow composition node
(`SequentialAgent`/`ParallelAgent`/`LoopAgent`/etc.) through the exact same
`execute(messages, user_message) -> AsyncGenerator[ExecutionEvent, None]`
shape as `AgentExecutor` runs a plain `Agent` - so anything that can be an
`Agent`'s entry point can be a workflow node's entry point too. `ncp.toml`
just points at a different kind of object:

    entry_point = "agents.main_agent:postmortem_pipeline"

instead of

    entry_point = "agents.main_agent:agent"

The pipeline itself is unchanged from `sequential-pipeline-agent` - three
steps, chained by default, with `share_state=True` so the last step can also
reach back two steps for `{incident_summary}`:

    summarize_incident  -> incident_summary
    draft_timeline      -> timeline
    draft_postmortem    -> the finished document

What changes is what happens on *every* turn. With a plain `Agent` as root,
an LLM triages first - it can answer "what can you do?" directly and only
runs the pipeline when the request warrants it. Here there is no triage step:
every message is step 1's input, unconditionally. That trade only makes sense
when the pipeline **is** the whole product - a single-purpose deployment with
no other behavior to gate - never when the agent also needs to handle
off-pipeline questions.
"""

from ncp import Agent, SequentialAgent
from tools.postmortem_tools import get_incident, get_incident_events


# =============================================================================
# Step 1: Summarize - the only step that looks the incident up
# =============================================================================

summarize_incident = Agent(
    name="summarize_incident",
    description="Retrieves an incident record and writes a factual summary",
    instructions="""You summarize network incidents.

The user's message contains an incident ID (e.g. INC-4471). Call get_incident
with it, then write a short factual summary covering: what broke, severity, how
long it lasted, which sites were affected, and the root cause.

Be concise and factual. No recommendations - a later step handles those.""",
    tools=[get_incident],
    output_key="incident_summary",
)


# =============================================================================
# Step 2: Timeline - receives step 1's summary as its input (chaining)
# =============================================================================

draft_timeline = Agent(
    name="draft_timeline",
    description="Builds a chronological timeline of an incident from its event log",
    instructions="""You build incident timelines.

You will receive a summary of an incident that includes its ID. Call
get_incident_events with that ID and turn the raw event log into a clean
chronological timeline.

Format each entry as `HH:MM - what happened`. Add a short note marking which
entry represents detection, which represents mitigation, and which represents
full recovery.""",
    tools=[get_incident_events],
    output_key="timeline",
)


# =============================================================================
# Step 3: Postmortem - needs BOTH the timeline (chained) and the summary
#         (two steps back, reachable only because share_state=True below)
# =============================================================================

draft_postmortem = Agent(
    name="draft_postmortem",
    description="Writes the final postmortem document",
    instructions="""You write blameless postmortem documents.

Here is the incident summary produced earlier in this pipeline:

{incident_summary}

You will separately receive the incident timeline as your input.

Using both, write a postmortem with these sections:
- **Summary** - what happened, in two or three sentences
- **Timeline** - the timeline you were given, tidied for readability
- **Root Cause** - the underlying cause, not just the trigger
- **Action Items** - three concrete preventive actions, each phrased as a task

Keep it blameless: describe systems and processes, never individuals.""",
    output_key="postmortem",
)


# =============================================================================
# The pipeline - this is the deployable entry point, not a plain Agent
# =============================================================================
# No wrapping Agent, no AgentTool: `ncp.toml`'s entry_point names this object
# directly, so every turn runs all three steps in order and the last step's
# output becomes the answer.

postmortem_pipeline = SequentialAgent(
    name="postmortem_pipeline",
    description="Summarizes an incident, builds its timeline, then writes the postmortem",
    sub_agents=[summarize_incident, draft_timeline, draft_postmortem],
    # Required for draft_postmortem's {incident_summary} placeholder: without
    # it, a step can only see its immediate predecessor's output.
    share_state=True,
)
