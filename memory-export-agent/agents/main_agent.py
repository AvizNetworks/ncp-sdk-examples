"""Main agent definition for memory-export-agent.

Demonstrates Memory().store(..., exportable=True): data stored this way can
be downloaded by the user as a raw CSV/JSON file - via the platform's
export_data_from_memory UI card, or its underlying REST endpoint
(GET /{conversation_id}/memory/{reference_id}/export?format=csv|json)
directly - bypassing the LLM and any HTML rendering entirely.

ui_components_enabled=True (scoped to just export_data_from_memory via
ui_components=[...]) is what makes that download card available to this
agent; it is not something you import or declare as a local @tool.
"""

from ncp import Agent
from tools.export_tools import generate_device_inventory, get_dataset_info


agent = Agent(
    name="MemoryExportAgent",
    description="Generates device inventory reports and lets the user download them as CSV/JSON",
    instructions="""You are a network inventory assistant.

You have two tools:
- generate_device_inventory(row_count=50, exportable=True): generates a
  synthetic device inventory and stores it in agent memory. Pass
  exportable=True (the default) so the user can download it as a file
  afterward; pass exportable=False to demonstrate what happens when a
  download is attempted on a non-exportable entry.
- get_dataset_info(reference_id): looks up metadata for a stored dataset,
  including whether it is exportable, without loading the full data.

When a user asks for an inventory report, call generate_device_inventory and
tell them how many devices were generated along with the reference_id. If
they then ask to download, export, or save it as a file, call the
export_data_from_memory tool with that reference_id - do not try to dump the
raw rows into the chat yourself. If they ask about a dataset without wanting
to download it, use get_dataset_info instead.""",
    tools=[generate_device_inventory, get_dataset_info],
    memory_store_enabled=True,
    ui_components_enabled=True,
    ui_components=["export_data_from_memory", "show_data_table_from_memory"],
)
