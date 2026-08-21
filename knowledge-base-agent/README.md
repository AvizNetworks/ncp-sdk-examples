# knowledge-base-agent

An NCP AI agent that answers questions from a bundled knowledge base, using
the SDK's `knowledge/` directory convention and the prebuilt
`peek_knowledge`/`search_knowledge` tools.

## What this example teaches

- How to ship documents with an agent in a `knowledge/` directory, and have
  the platform automatically ingest them into a per-agent ChromaDB
  collection at deploy time — no custom ingestion code required.
- How to give an agent the two prebuilt knowledge tools from
  `ncp.tools.knowledge`:
  - `peek_knowledge(limit=10)` — lists what's in the knowledge base (files,
    metadata, sample previews) without doing a search. Good for "what can
    you help me with?" style questions.
  - `search_knowledge(query, n_results=5, filters=None)` — semantic search
    over the knowledge base, optionally narrowed with metadata filters
    (e.g. `{"file_name": "faq.md"}`).

This agent's `knowledge/` directory contains three small docs about a
fictional product, "Nimbus Backup" — a FAQ, a troubleshooting guide, and a
glossary — so there's realistic, multi-file content to search across.

## Project Structure

```
knowledge-base-agent/
├── ncp.toml              # Project configuration
├── requirements.txt      # Python dependencies
├── agents/               # Agent definitions
│   ├── __init__.py
│   └── main_agent.py    # Registers peek_knowledge/search_knowledge as tools
└── knowledge/             # Documents ingested into the agent's knowledge base
    ├── faq.md
    ├── troubleshooting.md
    └── glossary.md
```

## Important: these tools only work after deploy

`peek_knowledge` and `search_knowledge` are **platform-provided tools**. The
copies importable from `ncp-sdk` are type stubs for IDE support — calling
them locally raises `NotImplementedError`. `ncp validate .` tolerates this
(it doesn't execute tools, just checks structure and imports), so a clean
`ncp validate` does **not** mean the knowledge base is working yet.

The real flow is:

1. `ncp package .` bundles `knowledge/*.md` into the `.ncp` archive along
   with the rest of the project — no manifest or extra config needed, any
   file under `knowledge/` ships automatically.
2. `ncp deploy` ingests those files into a ChromaDB collection scoped to
   this agent.
3. Only then, when the agent actually runs (`ncp playground` or `ncp ask`),
   do `peek_knowledge`/`search_knowledge` return real results.

## Quick Start

### 1. Authenticate with Platform

```bash
ncp authenticate
```

You'll be prompted for the platform URL, username, and password. Credentials
are stored locally (not committed to `ncp.toml`).

### 2. Validate Project

```bash
ncp validate .
```

Checks `ncp.toml`, the entry point, and that `agents/main_agent.py` imports
and defines an `Agent`. Passing here does not exercise `peek_knowledge`/
`search_knowledge` — see above.

### 3. Package Agent

```bash
ncp package . -o knowledge-base-agent.ncp
```

Creates `knowledge-base-agent.ncp`, including everything under `knowledge/`.

### 4. Deploy Agent

```bash
# First deployment
ncp deploy knowledge-base-agent.ncp

# Update an existing deployment
ncp deploy knowledge-base-agent.ncp --update
```

Deploying (or updating) re-ingests the current contents of `knowledge/` into
the agent's ChromaDB collection.

### 5. Test in Playground

```bash
ncp playground --agent knowledge-base-agent --show-tools
```

Try prompts like:

- "What topics does your knowledge base cover?" — exercises `peek_knowledge`
- "How do I fix a failed backup job with an authentication error?" —
  exercises `search_knowledge`
- "What's the difference between an incremental and a full backup?"
- "How long do you keep old file versions on the Pro plan?"

Exit playground with `Ctrl+C`.

## Adding your own documents

Drop additional `.md`, `.txt`, `.pdf`, or `.csv` files into `knowledge/` and
redeploy (`ncp package .` then `ncp deploy ... --update`) — each redeploy
re-ingests the current contents of the directory. There's no separate index
file to maintain.

## Troubleshooting

### `search_knowledge`/`peek_knowledge` raise `NotImplementedError`

You're running the agent's code directly with plain Python, or relying on
`ncp validate` to prove it works. These tools only function once the agent
is deployed and invoked through `ncp playground`/`ncp ask` against a real
platform.

### Search results don't reflect a document I just added

Make sure you re-ran `ncp package .` and `ncp deploy ... --update` after
adding the file — ingestion happens at deploy time, not automatically when
you edit local files.

### Authentication or deployment issues

```bash
ncp authenticate     # re-authenticate if credentials expired
ncp validate .        # check for structural issues first
ncp list               # confirm the agent actually deployed
```
