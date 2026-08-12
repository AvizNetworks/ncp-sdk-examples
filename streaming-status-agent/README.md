# Streaming Status Agent - Progress and Partial Output with send_status() / send_content()

**Demonstrates `send_status()` and `send_content()` (ncp-sdk >= 1.2.0): letting a long-running tool report progress to the UI while it's still running, instead of the UI staying blank until it returns.**

---

## 🎯 What This Example Teaches

1. **`send_status(message)`**: replaces a single status line in place - use it for overall progress ("Backing up host 3/50...")
2. **`send_content(chunk)`**: appends each chunk to a growing display - use it for partial results, the same way an LLM's own answer streams token by token
3. **Both are `async`**: they only work inside an `async def` tool that's executing on the platform - calling either elsewhere raises `RuntimeError`
4. **Observing them from the outside**: `AgentHooks.on_status_update` / `on_tool_stream` see every call as it happens, independent of the tool that made it

---

## 📁 Project Structure

```
streaming-status-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 Agent + hooks that log status/stream events
└── tools/
    ├── __init__.py
    └── backup_tools.py     # 🔧 backup_devices, get_stream_log, shared log
```

---

## 📡 The Tool: `tools/backup_tools.py`

```python
from ncp import send_content, send_status, tool

@tool
async def backup_devices(hostnames: list) -> dict:
    """Back up configuration for a list of network devices, reporting progress as it goes."""
    results = []
    total = len(hostnames)
    for i, host in enumerate(hostnames, start=1):
        await send_status(f"Backing up {host} ({i}/{total})...")
        # ... do the backup ...
        await send_content(f"- {host}: backup complete ({size_kb} KB)\n")
        results.append({"hostname": host, "status": "success", "size_kb": size_kb})

    await send_status(f"Backup complete: {total}/{total} devices")
    return {"backed_up": total, "results": results}
```

Note the tool is `async def` - both `send_status` and `send_content` are coroutines you `await`. Neither call changes the tool's return value; they're a side channel to the UI that runs *while* the tool is still executing.

### Why there's also a `get_stream_log` tool

`AgentHooks` callbacks (wired up in `agents/main_agent.py`) run wherever the agent executes, so their output isn't visible in your `ncp playground` terminal on its own (the same limitation described in `hooks-agent`'s README). This example's hooks log every `on_status_update` / `on_tool_stream` event into a shared list, and `get_stream_log()` hands that back to you as an ordinary tool result - a reliable way to confirm every status/content call actually fired, regardless of what your client renders live.

```python
hooks = AgentHooks(
    on_status_update=lambda data: log_stream_event(f"status_update type={data.status_type} message={data.status_message!r}"),
    on_tool_stream=lambda data: log_stream_event(f"tool_stream tool={data.tool_name} chunk={data.chunk!r}"),
)
```

---

## 🚀 Try It Out

```bash
cd streaming-status-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy streaming-status-agent.ncp
ncp playground --agent streaming-status-agent --show-tools
```

### Example: Back up a batch of devices, then inspect the stream

**You**: Back up switch-1, switch-2, and router-3

**Agent**: calls `backup_devices(["switch-1", "switch-2", "router-3"])` once, and returns a summary of what was backed up.

**You**: Show me the stream log

**Agent**: calls `get_stream_log()` and reports something like:

```
[09:12:01] status_update type=tool_start message='backup_devices'
[09:12:01] status_update type=custom message='Backing up switch-1 (1/3)...'
[09:12:01] tool_stream tool=backup_devices chunk='- switch-1: backup complete (24 KB)\n'
[09:12:01] status_update type=custom message='Backing up switch-2 (2/3)...'
[09:12:01] tool_stream tool=backup_devices chunk='- switch-2: backup complete (30 KB)\n'
[09:12:01] status_update type=custom message='Backing up router-3 (3/3)...'
[09:12:01] tool_stream tool=backup_devices chunk='- router-3: backup complete (17 KB)\n'
[09:12:02] status_update type=custom message='Backup complete: 3/3 devices'
```

Note the first `status_update` (`type=tool_start`) is emitted automatically before every tool call, before `backup_devices` ever calls `send_status()` itself (`type=custom`).

---

## 🎓 Key Takeaways

- `send_status()` = replace-in-place progress; `send_content()` = append-only partial output - use either or both
- Both only work on the platform (`async def` tool, real deployment) - they raise `RuntimeError` if you call them from a plain script
- `status_type` tells you whether a status update was automatic (`"tool_start"`) or tool-initiated (`"custom"`)
- `AgentHooks.on_status_update` / `on_tool_stream` let you observe this traffic centrally instead of instrumenting every tool

## 🚀 Next Steps

- Pair this with `hooks-agent` to see the full set of hook types side by side
- Pair with `handoff-agent`: hand off to this agent mid-conversation and watch the specialist stream its own progress
