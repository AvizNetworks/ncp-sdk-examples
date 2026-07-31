---
name: ncp-agent-dev
description: >-
  Build, deploy, test, and iterate on NCP SDK agents autonomously. Use whenever
  the task is to create or improve an agent with the `ncp` CLI / ncp-sdk —
  especially connector-backed agents (NetBox, Splunk, Elastic, etc.). Covers
  discovering data connectors, probing their tools, writing the agent, deploying,
  and running a structured test → iterate loop until it passes.
---

# NCP Agent Development (agent-driven)

You are building an NCP agent and driving the full loop yourself:
**discover → build → deploy → test → iterate**. Prefer the CLI primitives below
over guessing; they turn unknowns into facts.

## Prerequisites

- Authenticated: `ncp authenticate` (saves creds to `~/.ncp/credentials.toml`).
  Verify with `ncp list`. If it fails, ask the user to run `ncp authenticate`.
- Run `ncp` from the project's Python env (e.g. `./venv/bin/ncp`).

## The loop

```
ncp connectors list          # 1. discover the exact connector name
<probe tools>                # 2. learn the connector's tools (optional but recommended)
<write agent>                # 3. build with the correct name + tool-aware instructions
ncp validate                 # 4. static checks
ncp package . && ncp deploy   # 5. ship (add --update on redeploy)
ncp ask "..." --json         # 6. test — structured, scriptable
<evaluate + fix>             # 7. iterate until green
```

## 1. Discover connectors (never guess the name)

The `connectors=[...]` value must be the connector's **instance Name**, not its
type or tag. Get it from the platform, don't infer it:

```bash
ncp connectors list                 # Name, Type, Mode, Tags, Status
ncp connectors info NetboxEngg      # full details for one (name or id)
```

A connector that deploys but returns no data is almost always a wrong `Name`.

## 2. Probe the connector's tools (exploration agent)

Connector tools are provided at runtime by an MCP server, so learn them by
asking a throwaway probe agent bound to the connector:

```bash
ncp init _probe && cd _probe
# edit agents/main_agent.py:
#   connectors=["<ExactName>"], instructions="List and describe every tool you can call."
ncp package . && ncp deploy _probe.ncp
ncp ask "List every tool you can call. For each: exact tool name, what it does, and its parameters." \
  --agent _probe --json
ncp remove --agent _probe --yes    # clean up the probe when done
```

Record the real tool names + parameters — you'll write instructions that use
them correctly (e.g. avoid unsupported filters).

## 3. Write the agent

Minimal connector-backed agent:

```python
from ncp import Agent

agent = Agent(
    name="netbox-inventory-agent",
    description="Answers network inventory questions from NetBox DCIM/IPAM",
    instructions="""You are a network inventory assistant backed by NetBox.
Use the connector's tools to answer questions about devices, sites, IPAM, etc.

Accuracy rules (critical):
- NEVER guess or fabricate counts. Verify against the actual field.
- For "how many have/run X", inspect that specific field and count ONLY matches.
- Do NOT equate the total count with a filtered subset.
- If a field is empty/unset for some records, say so and how many — never assume.
- If an attribute isn't stored in the source, say it isn't recorded there.""",
    tools=[],
    connectors=["NetboxEngg"],
)
```

The **Accuracy rules** block is not boilerplate — connector agents hallucinate
counts without it (e.g. reporting "all 19 devices run SONiC" when the field is
unset). Keep it.

## 4–5. Validate, package, deploy

```bash
ncp validate
ncp package .
ncp deploy <name>.ncp            # first time
ncp deploy <name>.ncp --update   # every redeploy after that (else "already exists")
```

## 6. Test — structured and scriptable

`ncp ask` sends one question and returns `{answer, tools, tool_errors, error, ok}`.
Exit code is 0 when `ok`, 1 otherwise, so it composes in loops.

```bash
ncp ask "How many devices are in NetBox? List 5 with site and status." --agent netbox-inventory-agent --json
```

Build an eval set of questions with known-ish expectations, including:
- a straightforward query (does it call the right tool?),
- a **filtered count** (the classic hallucination trap),
- something the source does NOT store (it should decline, not invent).

Judge each answer: did it use a tool (`tools` non-empty when data was needed)?
any `tool_errors`? does the content match reality (cross-check with a direct
`ncp ask` diagnostic query)?

## 7. Iterate

When an answer is wrong: diagnose with a targeted follow-up question, fix the
**instructions** (or add/adjust a tool), bump the version in `ncp.toml`,
`ncp deploy --update`, and re-run the exact failing question plus a regression
pass. Repeat until the eval set is green.

## Cleanup

```bash
ncp remove --agent <name> --yes   # undeploy
```

## Primitives reference

| Need | Command |
|------|---------|
| Exact connector name | `ncp connectors list` / `ncp connectors info <name>` |
| Available platform agents | `ncp agents list` / `ncp agents info <name>` |
| Scaffold | `ncp init <name>` |
| Validate | `ncp validate` |
| Ship | `ncp package .` → `ncp deploy <pkg>.ncp [--update]` |
| Test (structured) | `ncp ask "<q>" --agent <name> --json` |
| Programmatic test | `from ncp.testing import ask_agent` → `AgentResult` |
| Undeploy | `ncp remove --agent <name> --yes` |
