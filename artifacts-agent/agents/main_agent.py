"""Main agent definition for artifacts-agent.

Demonstrates Artifacts().save_text() / save_file(): registering downloadable,
non-tabular files (a markdown report, a diagram the agent wrote to its own
local filesystem) - the counterpart to Memory(exportable=True) and its
export_data_from_memory UI card (see memory-export-agent), which only handle
tabular list[dict] records.

ui_components_enabled=True (scoped to just show_artifact_download_card via
ui_components=[...]) is what makes the download card available to this
agent; it is not something you import or declare as a local @tool.
"""

from ncp import Agent
from tools.artifact_tools import (
    collect_device_health,
    generate_health_report,
    generate_topology_diagram,
    get_artifact_info,
)


agent = Agent(
    name="ArtifactsAgent",
    description=(
        "Generates downloadable reports and diagrams as file artifacts "
        "(markdown, plain text, or any other file type)"
    ),
    instructions="""You are a network operations assistant.

You have four tools:
- collect_device_health(count=15): generates a synthetic per-device health
  snapshot and stores the raw rows in agent memory. This data is NOT
  directly exportable as CSV/JSON - it exists to feed generate_health_report.
- generate_health_report(reference_id, region="us-west"): reads a stored
  health snapshot and turns it into a downloadable markdown report artifact.
- generate_topology_diagram(region="us-west"): writes a small topology
  diagram to a file and registers it as a downloadable artifact - simulating
  a tool that produces its own file on disk (a real one might shell out to
  a diagram generator or draw an image). It does not need a memory reference.
- get_artifact_info(export_id): looks up metadata for a previously saved
  artifact (filename, size, type) without downloading it.

When a user asks for a health report, call collect_device_health first, then
generate_health_report with the reference_id it returns. When a user asks for
a topology diagram, call generate_topology_diagram directly. After either
tool returns an export_id, call show_artifact_download_card(export_id=...)
so the user sees a download card - do not try to paste the file contents
into the chat yourself. If they ask about a file without wanting to download
it, use get_artifact_info instead.""",
    tools=[
        collect_device_health,
        generate_health_report,
        generate_topology_diagram,
        get_artifact_info,
    ],
    memory_store_enabled=True,
    ui_components_enabled=True,
    ui_components=["show_artifact_download_card"],
)
