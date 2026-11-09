# files-agent

An NCP agent that answers questions about the user's files with the platform's
Files agent, and saves a report back as a file. It needs `ncp-sdk` 1.6.0 or
newer.

## What this example teaches

- `ncp.tools.files.ask_files(task, files=None, time_range=None, references=None)`
  hands a plain-language task to the platform's Files agent. It works across
  logs, configs, tables, documents and archives, and answers with evidence ids
  and coverage. The other tools in `ncp.tools.files` (`list_files`, `grep`,
  `sql`, `read_lines`, `search`, `find_entity`, `compare_files`,
  `describe_file`) are the steps it uses, for agents that want to drive them.
- `Files.upload(name, data, scope="project")` saves a file as the signed-in
  user. The platform decides as it does for a UI upload: a project member may
  upload to the current project, an organization admin may upload a system
  file. A refusal raises `FileUploadError`; `err.code` is `forbidden`,
  `unsupported_type`, `file_too_large`, and so on. `Files.wait_ready(file)`
  waits until the upload has been processed and can be searched.

## Access

The agent sees what the user sees in the UI and nothing more: the project's
files (when the chat is in a project), the organization's system files their
role may read, and the chat's attachments. Files are named by name, id or
`ref`, never by a path.

## Important: platform-only tools

`ask_files` and `Files` are platform-provided; the copies in `ncp-sdk` are
stubs, so calling them locally raises `NotImplementedError`. A clean
`ncp validate` only proves the structure and imports.

## Quick Start

```bash
ncp validate .
ncp package . -o files-agent.ncp
ncp deploy files-agent.ncp
ncp playground --agent files-agent --project 12 --show-tools
```

`--project <id>` runs the playground in a project you belong to, so the
project's files are reachable. Try:

- "List the files you can see and what each contains."
- "How many lines of dc1-fabric.log are errors, and what happened around the first one?"
- "Summarise the findings and save them as bgp-findings.md."
