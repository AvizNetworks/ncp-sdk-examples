# Artifacts Agent - Downloadable File Artifacts (Markdown, Diagrams, Any File)

**Demonstrates `Artifacts().save_text()`, `Artifacts().save_file()`, and `Artifacts().get_metadata()`: letting the user download an agent-generated file — a rendered report, a diagram, or any other non-tabular file — bypassing the LLM and the chat UI entirely.**

---

## 🎯 What This Example Teaches

1. **`Artifacts().save_text(...)`**: register markdown/plain-text/HTML content as a downloadable file
2. **`Artifacts().save_file(...)`**: register a file the agent already wrote to its own local filesystem as a downloadable file
3. **`Artifacts().get_metadata(...)`**: a cheap way to check a saved artifact's filename/size/type without downloading it
4. **`show_artifact_download_card`**: the platform UI tool that renders a "Download" card for any artifact, the counterpart to `export_data_from_memory`
5. **Where `Artifacts` fits next to `Memory`**: `Memory(exportable=True)` + `export_data_from_memory` only ever serve the *raw stored rows* as CSV/JSON/Excel. `Artifacts` is for everything that isn't tabular records — a report you rendered from that data, a diagram, a zip, a PDF.

If you haven't yet, see `ncp-sdk-examples/memory-export-agent` first for the tabular-data download flow (`Memory(exportable=True)` + `export_data_from_memory`) — this example only covers what's different for non-tabular files.

---

## 📁 Project Structure

```
artifacts-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 Agent, memory_store_enabled + ui_components_enabled
└── tools/
    ├── __init__.py
    └── artifact_tools.py    # 🔧 collect_device_health, generate_health_report,
                              #    generate_topology_diagram, get_artifact_info
```

---

## 📤 The Tools: `tools/artifact_tools.py`

**From data already in memory → a rendered report:**

```python
from ncp import Artifacts, Memory, tool

@tool
def generate_health_report(reference_id: str, region: str = "us-west") -> dict:
    """Turn a stored device health dataset into a downloadable markdown report."""
    rows = Memory().retrieve(reference_id)
    markdown = render_markdown_table(rows)  # simplified here
    return Artifacts().save_text(
        markdown,
        filename=f"{region}_health_report.md",
        description=f"Device health report for {region} ({len(rows)} devices)",
    )
```

**From a file the agent already wrote to disk:**

```python
@tool
def generate_topology_diagram(region: str = "us-west") -> dict:
    """Write a topology diagram to a file, then register it for download."""
    path = write_diagram_to_temp_file(region)  # simplified here
    try:
        return Artifacts().save_file(
            path,
            filename=f"{region}_topology.txt",
            description=f"Network topology diagram for {region}",
        )
    finally:
        os.remove(path)  # save_file() already copied the bytes
```

Both return the same shape: `success`, `export_id`, `filename`, `download_url`, `download_link`, `preview_url`, `file_size_bytes`.

## 🖼️ The Agent: `agents/main_agent.py`

```python
agent = Agent(
    name="ArtifactsAgent",
    description="...",
    instructions="...",
    tools=[collect_device_health, generate_health_report,
           generate_topology_diagram, get_artifact_info],
    memory_store_enabled=True,        # needed for Memory() (health data source)
    ui_components_enabled=True,       # opts in to the platform's UI visualization server
    ui_components=["show_artifact_download_card"],  # scope it to just the download card
)
```

`show_artifact_download_card` is **not** something you import or write — it's a platform-provided MCP UI tool (served by `ncp-mcp-ui-server`) that the platform attaches automatically once `ui_components_enabled=True`. It's the artifact-storage counterpart to `export_data_from_memory`: same card look, but sourced from a registered file artifact (`export_id`) instead of a memory-store dataset (`reference_id`).

### What happens when the user asks to download

1. The LLM calls `generate_health_report(...)` or `generate_topology_diagram(...)`, which calls `Artifacts().save_text()`/`save_file()` and gets back an `export_id`
2. The LLM calls `show_artifact_download_card(export_id=...)`
3. The tool looks up the artifact's filename/size/type and renders a card with a single **Download** button
4. Clicking it fetches `GET /projects/{project_id}/exports/{export_id}/download` (or `GET /exports/{export_id}/download` outside a project) directly — the file is streamed straight off disk into a `Content-Disposition: attachment` response. It never passes through the LLM.

---

## 🚀 Try It Out

```bash
cd artifacts-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy artifacts-agent.ncp
ncp playground --agent artifacts-agent --show-tools
```

### Example 1: A rendered report from stored data

**You**: Collect health data for 20 devices

**Agent**: calls `collect_device_health(count=20)`, reports the reference_id.

**You**: Now give me a health report for us-east

**Agent**: calls `generate_health_report(reference_id=..., region="us-east")`, then `show_artifact_download_card(export_id=...)` → a card with a single **Download** button appears; clicking it downloads `us-east_health_report.md`.

### Example 2: A file the agent wrote itself

**You**: Generate a topology diagram for us-east

**Agent**: calls `generate_topology_diagram(region="us-east")` (no memory reference needed — the file is written straight to disk), then `show_artifact_download_card(export_id=...)` → downloads `us-east_topology.txt`.

### Example 3: Check an artifact without downloading it

**You**: What do you know about that last file, without downloading it?

**Agent**: calls `get_artifact_info(export_id=...)`, returning `filename`, `file_size_bytes`, `file_type`, `status`.

---

## 🎓 Key Takeaways

- `Memory(exportable=True)` + `export_data_from_memory` → tabular `list[dict]` records only, served as CSV/JSON/Excel
- `Artifacts` → everything else: a rendered report, a diagram, a zip, a PDF — anything you can turn into bytes or already have as a file on disk
- `save_text()`/`save_bytes()`/`save_file()` all return the same shape (`export_id`, `download_url`, ...) so `show_artifact_download_card` doesn't care which one produced the artifact
- The download path is enforced server-side, not just hidden in the UI — the same `exported_files` REST endpoints used by the platform's own CSV/Excel/PDF export tools serve these artifacts too
- `get_metadata()` lets you (or the LLM) confirm a file's size/type cheaply, without re-reading it

## 🚀 Next Steps

- Combine with `memory-export-agent`'s pattern in the same agent: let the user choose between the raw CSV/JSON of a dataset (`Memory(exportable=True)`) and a rendered report built from it (`Artifacts().save_text()`)
- Try `Artifacts().save_bytes(...)` directly if your tool produces raw bytes (e.g. a PDF built with a library like `reportlab`) instead of a string or an on-disk file
- Drop the `ui_components=[...]` allowlist to see the full UI visualization toolset (interactive tables, charts, stat cards, the tabular export card) alongside the artifact download card
