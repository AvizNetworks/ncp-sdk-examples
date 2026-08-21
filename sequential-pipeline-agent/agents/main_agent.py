"""Main agent definition for sequential-pipeline-agent.

Demonstrates SequentialAgent: a fixed, ordered pipeline where each step's
output feeds the next. Unlike `multi-agent`'s AgentTool orchestrator - where an
LLM decides which specialist to call and when - a pipeline's order is decided by
you, at design time. Every run does the same steps in the same sequence.

The pipeline writes an incident postmortem in three steps:

    summarize_incident  -> incident_summary
    draft_timeline      -> timeline
    draft_postmortem    -> the finished document

Two different ways a step receives its input are both on display here:

1. **Chaining (the default).** Each step's input is simply the previous step's
   output text, like a Unix pipe. `draft_timeline` receives whatever
   `summarize_incident` produced without either agent being configured for it.

2. **`share_state=True` (opt-in).** The last step needs the *summary* as well as
   the timeline - that is two steps back, which chaining alone can't reach. With
   `share_state=True` every step's instructions get `{output_key}` placeholders
   filled in from all previously recorded outputs, so `draft_postmortem` can
   reference `{incident_summary}` directly.

Leave `share_state` off and that `{incident_summary}` placeholder is left as
literal text in the prompt - a useful thing to try, to see the difference.
"""

from ncp import Agent, AgentTool, SequentialAgent
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
# The pipeline
# =============================================================================

postmortem_pipeline = SequentialAgent(
    name="postmortem_pipeline",
    description="Summarizes an incident, builds its timeline, then writes the postmortem",
    sub_agents=[summarize_incident, draft_timeline, draft_postmortem],
    # Required for draft_postmortem's {incident_summary} placeholder: without
    # it, a step can only see its immediate predecessor's output.
    share_state=True,
)


# =============================================================================
# The deployable agent
# =============================================================================
# The entry point is a normal Agent that exposes the pipeline as one tool. That
# keeps the pipeline a *capability* the agent can choose to use, so it can also
# answer "what can you do?" without running a three-step pipeline to do it.

agent = Agent(
    name="postmortem_writer",
    description="Writes incident postmortems by running a multi-step drafting pipeline",
    instructions="""You help network engineers write incident postmortems.

When the user gives you an incident ID (e.g. "write a postmortem for INC-4471"),
call postmortem_pipeline with their request. It runs a three-step drafting
pipeline and returns the finished document - present it to the user as-is.

If the user asks something that isn't a postmortem request, answer directly
without calling the pipeline. Known incident IDs are INC-4471 and INC-4482.""",
    tools=[
        AgentTool(
            postmortem_pipeline,
            name="postmortem_pipeline",
            description=(
                "Run the full postmortem drafting pipeline for an incident. "
                "Pass the user's request including the incident ID."
            ),
        )
    ],
)
