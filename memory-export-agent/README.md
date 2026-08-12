# Memory Export Agent - Downloadable Datasets with exportable=True

**Demonstrates `Memory().store(..., exportable=True)` and `Memory().get_metadata()` (ncp-sdk >= 1.2.0): letting the user download an agent-memory dataset as a raw CSV/JSON file, bypassing the LLM and the chat UI entirely.**

---

## 🎯 What This Example Teaches

1. **`exportable=True`**: an opt-in flag on `Memory().store()` that marks an entry as user-downloadable
2. **`Memory().get_metadata()`**: a cheap way to check an entry's size, record count, and exportable status without loading its full payload
3. **`ui_components_enabled` + `ui_components`**: how a custom agent opts in to the platform's UI visualization server and scopes it to just the tool it needs
4. **What "exportable" actually gates**: a real REST download endpoint, not just something the model can decide to show

If you haven't yet, see `ncp-sdk-examples/memory-store-agent` first for the base `Memory` API (`store`/`retrieve`/`list_entries`/`delete`) - this example only covers what's new on top of that.

---

## 📁 Project Structure

```
memory-export-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 Agent, memory_store_enabled + ui_components_enabled
└── tools/
    ├── __init__.py
    └── export_tools.py     # 🔧 generate_device_inventory, get_dataset_info
```

---

## 📤 The Tools: `tools/export_tools.py`

```python
from ncp import Memory, tool

@tool
def generate_device_inventory(row_count: int = 50, exportable: bool = True) -> dict:
    """Generate a synthetic device inventory report and store it in agent memory."""
    rows = _generate_inventory(row_count)
    reference_id = Memory().store(
        data=rows,
        data_type="device_inventory",
        description=f"Device inventory report ({row_count} devices)",
        exportable=exportable,
    )
    return {"reference_id": reference_id, "record_count": len(rows), "exportable": exportable}

@tool
def get_dataset_info(reference_id: str) -> dict:
    """Look up metadata for a stored dataset without loading its full payload."""
    return Memory().get_metadata(reference_id)
```

`exportable` defaults to `False` on `Memory().store()` - this agent's tool exposes it explicitly so you can compare an exportable entry against a non-exportable one in the same conversation.

## 🖼️ The Agent: `agents/main_agent.py`

```python
agent = Agent(
    name="MemoryExportAgent",
    description="...",
    instructions="...",
    tools=[generate_device_inventory, get_dataset_info],
    memory_store_enabled=True,        # required to use Memory() at all
    ui_components_enabled=True,       # opts in to the platform's UI visualization server
    ui_components=["export_data_from_memory"],  # scope it to just the download-card tool
)
```

`export_data_from_memory` itself is **not** something you import or write - it's a platform-provided MCP UI tool (served by `ncp-mcp-ui-server`) that the platform attaches automatically once `ui_components_enabled=True`. `ui_components=[...]` is an optional allowlist; omit it to expose every UI tool (interactive tables, charts, stat cards, etc.) instead of just this one.

### What happens when the user asks to download

1. The LLM calls `export_data_from_memory(reference_id=...)`
2. The tool does a cheap metadata-only lookup and checks `exportable` - if the entry isn't exportable, or has expired, it renders an explanatory card instead of a download link
3. If exportable, it renders a card with **Download CSV** / **Download JSON** buttons
4. Clicking a button calls `GET /{conversation_id}/memory/{reference_id}/export?format=csv|json` directly - the data is streamed straight from Redis into a `Content-Disposition: attachment` response. It never passes through the LLM, and never gets reshaped into HTML.

---

## 🚀 Try It Out

```bash
cd memory-export-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy memory-export-agent.ncp
ncp playground --agent memory-export-agent --show-tools
```

### Example 1: Generate and download

**You**: Generate an inventory report for 30 devices

**Agent**: calls `generate_device_inventory(row_count=30)`, reports the reference_id and record count.

**You**: Download that as a file

**Agent**: calls `export_data_from_memory(reference_id=...)` → a card with Download CSV / Download JSON buttons appears; clicking either downloads the 30-row report directly.

### Example 2: A non-exportable entry

**You**: Generate a 10-device report, but don't make it exportable

**Agent**: calls `generate_device_inventory(row_count=10, exportable=False)`.

**You**: Now download it

**Agent**: calls `export_data_from_memory(reference_id=...)` → the card explains the dataset isn't marked as exportable, instead of offering a download.

### Example 3: Check metadata first

**You**: What do you know about that last dataset, without loading it?

**Agent**: calls `get_dataset_info(reference_id=...)`, returning `record_count`, `size_bytes`, `schema_hint`, `exportable`, etc.

---

## 🎓 Key Takeaways

- `exportable=True` is opt-in per entry, at store time - decide up front which datasets should be user-facing downloads
- The export path is enforced server-side (the REST endpoint re-checks `exportable`), not just hidden in the UI - a model can't talk its way around it
- `get_metadata()` / `get_dataset_info` let you (or the LLM) inspect an entry's shape and export status cheaply, without paying to decompress a large payload
- UI tools like `export_data_from_memory` are platform capabilities you opt into (`ui_components_enabled`), not something you write yourself

## 🚀 Next Steps

- Combine with `memory-store-agent`'s pattern: generate a large dataset, summarize it for the LLM with a processing tool, and separately mark it `exportable=True` so the user can still get the raw rows
- Drop the `ui_components=[...]` allowlist to see the full UI visualization toolset (interactive tables, charts, stat cards) alongside the export card
