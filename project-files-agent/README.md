# project-files-agent

An NCP agent that answers questions from the files users upload to a
**project**: design documents, device inventories and logs. It uses the
platform's prebuilt project file tools from `ncp.tools.knowledge_base`, the
same tools NCP's own file agent uses. It ships no custom tools or ingestion
code.

## What this example teaches

- How to give an agent RAG over a project's uploaded files by importing
  prebuilt tools. Files are chunked and embedded when they are uploaded to the
  project, so the agent doesn't ingest anything itself.
- How these tools differ from `ncp.tools.knowledge` (see
  [knowledge-base-agent](../knowledge-base-agent)):

  | | `ncp.tools.knowledge` | `ncp.tools.knowledge_base` |
  |---|---|---|
  | Searches | the agent's own `knowledge/` directory | files users upload to the project |
  | Indexed | when the agent is deployed/onboarded | when a file is uploaded |
  | Scoped to | the agent | the project the chat runs in |

- How to pick the right tool for each kind of question, and combine them:

  | Tool | Use it for |
  |---|---|
  | `list_project_files()` | What files exist, their summaries, true row counts, columns and SQL table names |
  | `search_project_knowledge_base(query, filenames=None, metadata_filters=None, n_results=10)` | Questions about meaning in documents (RAG) |
  | `query_project_file(sql, filename=None, sheet=None, max_rows=100)` | Exact answers from CSV/Excel: counts, filters, dates, JOINs |
  | `search_file_content(pattern, filenames=None, max_matches=100, context_lines=0, case_sensitive=False)` | Regex search over logs and text files |
  | `read_file_lines(filename, start_line=1, end_line=None)` | The lines around a `search_file_content` hit |

## Project Structure

```
project-files-agent/
├── ncp.toml                  # Project configuration
├── requirements.txt          # Intentionally empty (see below)
├── .ncpignore                # Keeps sample-project-files/ out of the package
├── agents/
│   ├── __init__.py
│   └── main_agent.py         # Registers the five project file tools
└── sample-project-files/     # Upload these to a project to try the agent
    ├── dc1-fabric-design.md  # Design standard: routing, MTU, approved releases, EOL policy
    ├── dc1-inventory.csv     # 12 devices: vendor, model, OS version, EOL date
    └── dc1-fabric.log        # 3 days of fabric syslog: BGP drops, link flaps, MTU mismatch
```

`sample-project-files/` is **not** a `knowledge/` directory. Those files are
data for a project, uploaded through the UI. They are not part of the agent.

## Important: the tools need a project

The tools always search the project the conversation runs in. The agent never
passes a project ID and can't see other projects' files. That has two
consequences:

- **Use the agent from a project chat.** It works when users pick it directly
  in a project's chat, and when the orchestrator calls it for them.
- **The SDK playground doesn't work.** `ncp playground` runs with no project,
  so every tool returns *"No project context available"*.

As with every platform tool, the copies in `ncp-sdk` are type stubs for IDE
support and `ncp validate`. Calling them locally raises `NotImplementedError`.

## Quick Start

### 1. Authenticate with the platform

```bash
ncp authenticate
```

### 2. Validate and package

```bash
ncp validate .
ncp package . -o project-files-agent.ncp
```

This needs an `ncp-sdk` release that includes `ncp.tools.knowledge_base`.

### 3. Onboard the agent

An admin onboards it, either in the UI (**Agents** page, upload
`project-files-agent.ncp`) or from the CLI:

```bash
ncp onboard project-files-agent.ncp
# later: ncp onboard project-files-agent.ncp --update
```

Then grant it to roles in **Admin > Roles & Permissions** (`CustomAgents`).

### 4. Upload the sample files to a project

Open a project, upload the three files from `sample-project-files/`, and wait
until each one has finished processing. A file still processing isn't
searchable yet.

### 5. Ask questions in the project chat

Mention the agent by its onboarded name, `@project-files-agent` (the `name`
in `ncp.toml`), or let the orchestrator route to it.
Each question below has one right answer in the sample files:

| Question | Tools it should use | Expected answer |
|---|---|---|
| What files are in this project and what's in them? | `list_project_files` | 3 files; the inventory has 12 rows |
| What MTU should fabric links use, and when is the maintenance window? | `search_project_knowledge_base` | 9214 bytes; Sunday 02:00–04:00 UTC |
| How many Arista leaves are there? | `query_project_file` | 4 (`leaf-01`…`leaf-04`; border leaves are a separate role) |
| Which devices are not on the approved software release? | `search_project_knowledge_base` + `query_project_file` | `leaf-03` (EOS 4.30.5M), `leaf-07` (NX-OS 10.2(5)), `bleaf-02` (EOS 4.31.1F) |
| As of 2026-10-08, which devices are past EOL, and which are within 180 days of it? | `search_project_knowledge_base` + `query_project_file` | Past EOL: `leaf-05`, `leaf-06` (P1 risk). Within 180 days: `leaf-07`, `leaf-08` |
| How many times did leaf-07's BGP session go down, and why? | `search_file_content` (+ `read_file_lines`) | 3 times, hold timer expired; twice right after Ethernet1/49 lost link |
| Which leaves lost BGP sessions to hold-timer expiry, and are they on the approved release? | `search_file_content` + `query_project_file` + `search_project_knowledge_base` | `leaf-03` and `leaf-07`. Neither is on the approved release |
| Is there an MTU problem anywhere? | `search_file_content` + `search_project_knowledge_base` | `leaf-01` Ethernet49/1 at 1500 vs peer 9214, a design violation |

To see which tools actually ran, open the message's agent trace in the chat.

## requirements.txt is intentionally empty

Onboarded agents run inside the platform, and onboarding `pip install`s
`requirements.txt` into the platform itself. The platform already provides the
real `ncp` package, so don't list `ncp-sdk` there. Install it locally for
`ncp validate` and `ncp package` only.

## Adapting it

- **Your own files:** nothing to change. The agent works on whatever the
  project holds.
- **Fewer tools:** for a docs-only agent, keep `list_project_files` and
  `search_project_knowledge_base`. For a log-only agent, keep
  `search_file_content` and `read_file_lines`.
- **Combine with your own tools:** add the project file tools to any agent's
  `tools=[...]` list next to your own `@tool` functions.

## Troubleshooting

### Every tool returns "No project context available"

The agent is running outside a project, most likely in `ncp playground`. Ask
from a chat inside a project.

### A file I uploaded isn't found

Check that it has finished processing in the project's file list. Note what
gets indexed for search:

- PDF, DOCX, Markdown, HTML and text/log files are chunked.
- CSV and Excel files contribute a profile and sample rows. Use
  `query_project_file` for exact answers about them.
- `.doc`, `.ppt` and `.pptx` upload fine but are never chunked, so semantic
  search can't see their contents.

### Counts look wrong

The agent may be counting `search_project_knowledge_base` hits. Those are a
handful of similar chunks, not the file. The instructions tell it to use
`query_project_file` for counts; keep that guidance if you edit them.
