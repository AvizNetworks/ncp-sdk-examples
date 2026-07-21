# memory-store-agent

An NCP SDK agent that demonstrates how to use the **agent memory store** to
handle large datasets without overflowing the LLM context window.

---

## What This Example Teaches

- How to enable agent memory on an SDK agent (`memory_store_enabled`, `memory_tools_enabled`, `memory_context_enabled`)
- How to store large tool results in Redis-backed memory using `Memory().store()`
- How to retrieve stored data inside a tool for **server-side processing** with `Memory().retrieve()`
- How to return only a small summary to the LLM instead of thousands of rows
- How to list stored datasets with `Memory().list_entries()` and clean up with `Memory().delete()`
- How to connect an Elasticsearch (or any) MCP server and have its results stored automatically

---

## The Core Problem

When a tool returns thousands of rows, all of it goes into the LLM context window.
A 5,000-row Elasticsearch result can consume the entire context budget — leaving no
room for the agent to reason or respond.

```
WITHOUT memory store:
  ES query → 5,000 rows → ToolMessage (huge) → context full → agent fails
```

The agent memory store solves this by keeping large payloads in Redis. The LLM
receives a lightweight reference instead of the full data:

```
WITH memory store:
  ES query → 5,000 rows → stored in Redis → reference_id + 25-row preview → context safe
                                                       ↓
                               LLM calls top_talkers(reference_id="abc12345")
                                                       ↓
                               tool retrieves 5,000 rows internally
                               → aggregates → returns top 10 rows
                                                       ↓
                               LLM sees 10 rows — context stays healthy
```

---

## Project Structure

```
memory-store-agent/
├── ncp.toml                    # Project config and entry point
├── requirements.txt            # Python dependencies
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # Agent definition with memory flags
└── tools/
    ├── __init__.py
    └── flow_tools.py           # Memory store usage: store, retrieve, list, delete
```

---

## Key Files

| File | Purpose |
|---|---|
| `agents/main_agent.py` | Defines the agent with `memory_store_enabled=True` and all processing tools |
| `tools/flow_tools.py` | Five tools demonstrating the full memory lifecycle |

---

## The Memory Flags

```python
agent = Agent(
    name="FlowAnalystAgent",
    ...
    memory_store_enabled=True,   # Store large tool results in Redis
    memory_tools_enabled=True,   # Inject retrieve_memory / list_memory_entries automatically
    memory_context_enabled=True, # Surface stored entries as a table in the system prompt
)
```

All three default to `False` — opt in explicitly when your agent handles large data.

| Flag | What it does |
|---|---|
| `memory_store_enabled` | When the LLM sets `_store_in_memory=true` on a tool call, the executor stores the result in Redis and replaces the ToolMessage with a reference (8-char ID + row count + schema + 25-row preview) |
| `memory_tools_enabled` | Platform injects `retrieve_memory`, `list_memory_entries`, `get_memory_details`, `delete_memory` as built-in tools |
| `memory_context_enabled` | A table of all stored entries is injected into the system prompt so the LLM knows what datasets are available |

---

## Tool Walkthrough

### `generate_flow_data` — store large data explicitly

```python
@tool
def generate_flow_data(device_count: int = 10, records_per_device: int = 100) -> Dict[str, Any]:
    """Generate synthetic network flow records and store them in agent memory."""
    records = _generate_records(device_count, records_per_device)

    reference_id = Memory().store(
        data=records,
        data_type="network_flows",
        description=f"Synthetic flow data — {device_count} devices × {records_per_device} records",
    )

    return {
        "reference_id": reference_id,   # ← LLM receives this, not the records
        "record_count": len(records),
    }
```

The LLM never sees the raw records — only the `reference_id` and metadata.

### `top_talkers` — retrieve and process server-side

```python
@tool
def top_talkers(reference_id: str, top_n: int = 10) -> Dict[str, Any]:
    """Find the top N source IPs by bytes — processes data server-side."""
    records = Memory().retrieve(reference_id)   # ← full dataset retrieved internally

    aggregated = {}
    for rec in records:
        src = rec["src_ip"]
        aggregated.setdefault(src, {"total_bytes": 0, "flow_count": 0})
        aggregated[src]["total_bytes"] += rec["bytes"]
        aggregated[src]["flow_count"] += 1

    ranked = sorted(aggregated.items(), key=lambda x: x[1]["total_bytes"], reverse=True)
    return {"top_talkers": [...ranked[:top_n]...]}   # ← only top N rows returned to LLM
```

The 5,000 rows are fetched from Redis inside the tool function. The LLM context
only ever sees the final 10-row summary.

### `list_datasets` — discover what's in memory

```python
@tool
def list_datasets(data_type: Optional[str] = None) -> Dict[str, Any]:
    """List all datasets currently stored in agent memory."""
    entries = Memory().list_entries(data_type=data_type)
    return {"datasets": entries, "count": len(entries)}
```

### `drop_dataset` — clean up when done

```python
@tool
def drop_dataset(reference_id: str) -> Dict[str, Any]:
    """Delete a stored dataset from agent memory."""
    Memory().delete(reference_id)
    return {"deleted": True, "reference_id": reference_id}
```

---

## Memory Lifecycle

```
Memory().store(data, ...)     →  reference_id  (data in Redis, TTL 1 hour)
Memory().retrieve(ref_id)     →  original data
Memory().list_entries(...)    →  [metadata, ...]  (no data payloads)
Memory().get_metadata(ref_id) →  single metadata dict
Memory().delete(ref_id)       →  None  (entry removed)
```

**Limits:**
- Entry TTL: **1 hour** (conversation-scoped, expires automatically)
- Max entry size: **50 MB** (ValueError raised if exceeded)
- Auto-compression: above **512 KB** (transparent zlib)
- Scope: per conversation — isolated per user session

---

## Connecting to a Real Elasticsearch MCP

Uncomment the `mcp_servers` block in `agents/main_agent.py` to connect to an
Elasticsearch MCP server. Results from ES tools will be stored in memory
automatically when `memory_store_enabled=True` — no code changes needed.

```python
agent = Agent(
    ...
    memory_store_enabled=True,
    mcp_servers=[
        MCPConfig.streamable_http(
            url="http://elastic-mcp:8080",
            headers={"Authorization": "Bearer YOUR_TOKEN"},
        )
    ],
)
```

When the LLM queries Elasticsearch and sets `_store_in_memory=true` on the tool
call, the executor stores the full result in Redis and the agent processes
it the same way — via `reference_id`.

---

## Running This Example

```bash
cd memory-store-agent
pip install -r requirements.txt

# Authenticate with your NCP platform
ncp authenticate

# Test in the playground
ncp playground

# Deploy to the platform
ncp deploy
```

Try these prompts in the playground:

```
Generate 1000 flow records and show me the top 10 source IPs by bytes
```

```
What datasets are stored in memory right now?
```

```
Show me the protocol breakdown for the dataset you just created
```

```
Delete the flow dataset when you're done with the analysis
```

---

## Key Takeaways

1. **`Memory().store()` keeps large data out of context** — return a `reference_id`, not the data
2. **Processing tools take `reference_id` as input** — retrieve internally, return only summaries
3. **Three memory flags work together** — `store_enabled` + `tools_enabled` + `context_enabled`
4. **Memory is conversation-scoped and ephemeral** — 1-hour TTL, not persistent across sessions
5. **`Memory().delete()` is good hygiene** — free up Redis when analysis is done
6. **MCP tools benefit automatically** — `memory_store_enabled=True` covers both SDK tools and MCP tools

---

## Next Steps

- Connect a real Elasticsearch or NetFlow MCP server (see the commented block in `main_agent.py`)
- Add more analysis tools: `anomaly_detection`, `geo_breakdown`, `port_scan_detection`
- Chain analysis: store intermediate results and build multi-step pipelines
- Combine with `invoke_llm()` to generate natural-language summaries of stored datasets
