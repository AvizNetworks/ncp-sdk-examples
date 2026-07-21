"""Main agent definition for memory-store-agent.

This agent demonstrates how to use the NCP agent memory store to handle
large datasets without overflowing the LLM context window.

The core pattern:
  1. A tool fetches a large dataset and stores it in memory → returns a reference_id
  2. Processing tools receive the reference_id, retrieve the data internally,
     and return only a small summarised result to the LLM
  3. The LLM context never sees the full dataset — only summaries and reference IDs

This example uses synthetic network flow data to keep things self-contained.
To connect to a real Elasticsearch instance, uncomment the mcp_servers block below.
"""

from ncp import Agent, MCPConfig
from tools.flow_tools import (
    generate_flow_data,
    top_talkers,
    protocol_breakdown,
    list_datasets,
    drop_dataset,
)


agent = Agent(
    name="FlowAnalystAgent",
    description=(
        "Analyses network flow data stored in agent memory. "
        "Handles large datasets without context overflow by processing data server-side."
    ),
    instructions="""You are a network flow analyst with access to an agent memory store.

## How memory works in this agent

When tools fetch large datasets (potentially thousands of flow records), the results
are stored in Redis-backed memory rather than returned inline. You receive a lightweight
reference_id instead of the full data. This prevents context overflow.

Use the reference_id with processing tools to compute summaries server-side:
- Only the final summary (e.g., top 10 rows) comes back to you
- The full dataset stays in memory, accessible by reference_id
- Memory entries expire after 1 hour

## Your tools

**generate_flow_data(device_count, records_per_device)**
Generate synthetic network flow records and store them in memory.
Returns a reference_id. Use this to create a dataset to analyse.

**top_talkers(reference_id, top_n)**
Find the top N source IP addresses by total bytes transferred.
Retrieves and processes data server-side — you see only the summary.

**protocol_breakdown(reference_id)**
Group flow records by protocol and sum bytes per protocol.
Useful for understanding traffic composition.

**list_datasets()**
List all datasets currently stored in memory for this conversation.
Shows reference_id, description, record count, and creation time.

**drop_dataset(reference_id)**
Delete a stored dataset when it is no longer needed.

## Workflow example

User: "Generate 500 flow records and show me the top 5 talkers"
1. Call generate_flow_data(device_count=10, records_per_device=50)
   → Returns {"reference_id": "abc12345", "record_count": 500}
2. Call top_talkers(reference_id="abc12345", top_n=5)
   → Returns top 5 rows — full 500-record dataset never enters context

## Tips

- Always pass the exact reference_id string returned by generate_flow_data
- Use list_datasets() if you are unsure what data is currently in memory
- Call drop_dataset() after finishing analysis to free up memory
- Memory is conversation-scoped — a new conversation starts with empty memory
""",
    tools=[
        generate_flow_data,
        top_talkers,
        protocol_breakdown,
        list_datasets,
        drop_dataset,
    ],
    memory_store_enabled=True,
    memory_tools_enabled=True,
    memory_context_enabled=True,

    # Uncomment to connect to a real Elasticsearch MCP server.
    # Flow records returned by ES tools will also be stored in memory
    # automatically when the LLM sets _store_in_memory=true on the tool call.
    #
    # mcp_servers=[
    #     MCPConfig.streamable_http(
    #         url="http://elastic-mcp:8080",
    #         headers={"Authorization": "Bearer YOUR_TOKEN"},
    #     )
    # ],
)
