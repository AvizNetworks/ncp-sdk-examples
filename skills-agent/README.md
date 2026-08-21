# skills-agent

An NCP AI agent that uses three **Agent Skills** — `SKILL.md` files bundled
in a `skills/` directory — to carry three distinct network-triage workflows,
instead of baking all three into the agent's always-loaded `instructions`.

## What this example teaches

- How to ship procedural knowledge with an agent in a `skills/` directory
  (a project-local convention, undeclared in `ncp.toml` — same pattern as
  `knowledge/`, see `knowledge-base-agent`), and reference it by name from
  `Agent(skills=[...])`.
- What a `SKILL.md` looks like: YAML frontmatter (`name`, `description` —
  the `description` is what the platform matches the user's request
  against, so it states both *what* the skill does and *when* to use it)
  plus a markdown body with the actual step-by-step instructions.
- **Why more than one skill matters.** With a single skill, an agent has
  nothing to *choose between* — this example's three skills
  (`device-triage`, `interface-flapping-diagnosis`, `capacity-check`) cover
  three symptoms that call for different tool sequences and different
  conclusions from the same three device tools. The agent has to read each
  skill's `description` and pick the one that actually matches the user's
  report — see "With skills vs. without" below for what this costs (and
  saves) in context.
- The difference between `instructions` (always loaded into every turn's
  system prompt) and a skill's body (only loaded when the agent calls
  `read_skill`) — this agent's `instructions` are deliberately short and
  don't even name the three skills; the platform injects that list itself.
- That `ncp validate` lints every `SKILL.md`'s frontmatter and cross-checks
  every name an agent declares in `skills=[...]` against what's actually on
  disk under `skills/`, catching a typo locally instead of at deploy time.

This agent's four tools (`get_device_inventory`, `ping_device`,
`check_interface_status`, `get_interface_utilization`) return simulated,
deterministic data for three fake devices — no real network access or
connector needed, so you can run the whole example end-to-end without a lab
network.

## The three skills

| Skill | Triggers on | Workflow |
|---|---|---|
| `device-triage` | "is this device down/unreachable?" | inventory → reachability, stop if unreachable |
| `interface-flapping-diagnosis` | "this interface is flapping/erroring" | reachability → error counters → CRC vs. drops interpretation |
| `capacity-check` | "is this link saturated/need an upgrade?" | reachability → utilization → threshold band → rule out errors as the real cause |

All three call the *same* small toolset in different orders and interpret
the results differently — the skills aren't giving the agent new
capabilities (that's what tools are for), they're giving it three different
**procedures** for using the capabilities it already has. `capacity-check`
even points the agent at `interface-flapping-diagnosis` by name in its own
body (step 4) when it detects the utilization reading might actually be an
error condition — skills can reference each other, the same way a human
runbook says "see the other runbook for X."

## With skills vs. without

If these three workflows were pasted directly into `instructions` instead
of split into skills, here's what actually happens on every single turn,
measured from this project's real files:

| | Always loaded (every turn) | Loaded only when relevant |
|---|---|---|
| **With skills** (this project) | 3 × name+description ≈ **240 tokens** | one skill's body ≈ **380–500 tokens**, only when the agent decides it's relevant, 0 otherwise |
| **Without skills** (all three inlined into `instructions`) | all three full bodies ≈ **1,300 tokens**, on *every* turn regardless of relevance | — |

That's the whole tradeoff: asking this agent something that needs none of
the three workflows (`"what's core-sw-01's vendor and model?"`) costs this
project's `skills=[...]` version only the ~240 tokens of always-loaded
metadata — a monolithic-instructions version would still be paying the
full ~1,300 tokens of workflow text you never used, every single turn,
whether it's relevant or not. That gap gets strictly worse as you add more
skills — a fourth skill costs this project one more name+description line
(~90 tokens) always-loaded; it would cost another full workflow's worth of
tokens (400–700+) on *every* turn if inlined instead, whether or not that
turn ever needed it.

The other cost of the "inline everything" approach doesn't show up in a
token count at all: with three unrelated workflows concatenated into one
`instructions` string, the model has to figure out on its own, from prose,
which paragraph applies to the current request — the same ambiguity a human
would have skimming one giant runbook instead of picking the right
five-page document off a shelf. Splitting into skills makes that choice an
explicit, cheap first step (`read_skill(name)`) instead of an implicit one
buried in a wall of always-present text.

## Project Structure

```
skills-agent/
├── ncp.toml                            # Project configuration
├── requirements.txt                     # Python dependencies
├── agents/
│   ├── __init__.py
│   └── main_agent.py                    # Declares all three skill names
├── tools/
│   ├── __init__.py
│   └── device_tools.py                  # Simulated device/interface/utilization checks
└── skills/                              # Agent Skills (undeclared in ncp.toml)
    ├── device-triage/
    │   └── SKILL.md
    ├── interface-flapping-diagnosis/
    │   └── SKILL.md
    └── capacity-check/
        └── SKILL.md
```

## Important: `read_skill`/`read_skill_reference` only exist once deployed

`Agent.skills` is structural-only in the SDK — declaring
`skills=[...]` does **not** resolve or load anything locally.
`ncp validate .` checks that each `skills/<name>/SKILL.md` exists and is
well-formed, but it doesn't run the agent, so it doesn't prove any skill
actually triggers.

The real flow is:

1. `ncp package .` bundles all three `skills/*/SKILL.md` into the `.ncp`
   archive along with the rest of the project — no manifest or extra config
   needed, any directory under `skills/` ships automatically (same as
   `knowledge/`).
2. `ncp deploy` (or an admin `ncp onboard`) makes each skill's name
   resolvable on the platform.
3. Only then, when the agent actually runs, does the platform add a
   `read_skill`/`read_skill_reference` tool pair to the agent and surface an
   "## Available Skills" section (name + description only, for all three)
   in its system prompt — the agent has to call `read_skill(name)` on
   whichever one it thinks applies to see that skill's actual workflow.

## Quick Start

### 1. Authenticate with Platform

```bash
ncp authenticate
```

### 2. Validate Project

```bash
ncp validate .
```

Look for a `🧩 Validating skills...` section reporting all three:
`✓ skills/capacity-check`, `✓ skills/device-triage`,
`✓ skills/interface-flapping-diagnosis`. Try renaming a skill's directory
(or the `name` in its frontmatter) without updating `agents/main_agent.py`
to see the "declares unknown skill" error this check catches.

### 3. Package Agent

```bash
ncp package . -o skills-agent.ncp
```

### 4. Deploy Agent

```bash
ncp deploy skills-agent.ncp
# or, to update an existing deployment:
ncp deploy skills-agent.ncp --update
```

### 5. Test in Playground

```bash
ncp playground --agent skills-agent --show-tools --logs
```

Try prompts that should each trigger a *different* skill, so you can watch
the agent actually choose between them (with `--logs`, look for which
`read_skill` name it calls first):

- **`device-triage`**: "edge-sw-07 is down, can you confirm?" — stops after
  the reachability check per the skill's "don't check interfaces on an
  unreachable device" rule.
- **`interface-flapping-diagnosis`**: "Gi1/0/3 on access-sw-12 keeps
  flapping, what's wrong with it?" — surfaces the simulated CRC errors and
  should conclude "physical layer / cable / transceiver," not "duplex
  mismatch."
- **`capacity-check`**: "is the uplink Te1/1/1 on core-sw-01 saturated?" —
  should report ~92% utilization and recommend an upgrade now.
- **Cross-skill case**: "is Gi1/0/3 on access-sw-12 running out of
  bandwidth?" — utilization there is low (~22%) but the interface has real
  CRC errors; a good answer flags the errors rather than declaring it a
  capacity problem — this is `capacity-check` step 4 in action.
- **No skill needed**: "what vendor and model is core-sw-01?" — answerable
  from `get_device_inventory` alone; watch that the agent doesn't call
  `read_skill` at all for this one.

With `--show-tools`, you should see `read_skill`/`read_skill_reference`
alongside the four device tools.

## Adding your own skills

Add another subdirectory under `skills/` with its own `SKILL.md`, reference
its name in `Agent(skills=[...])`, and redeploy. `ncp validate` will catch a
missing/misnamed skill before you package it. As you add more, keep each
skill's `description` narrow and non-overlapping with the others (see how
`device-triage`'s description explicitly excludes what the other two
cover) — an ambiguous `description` is what actually causes wrong-skill
selection, not a tooling problem.

## Troubleshooting

### `ncp validate` doesn't show a "Validating skills" section

You're likely running an older `ncp-sdk` that predates the Skills feature —
see the note in `requirements.txt` about installing from the local
`ncp-sdk` checkout until it's published.

### The agent calls the wrong skill, or none at all

Check the `description` fields for overlap or vagueness first — skill
selection is the model reading short descriptions and guessing, so a vague
or overlapping one is the most common cause. `--show-tools`/`--logs` in
playground will show you exactly which (if any) `read_skill` call happened.

### The agent never calls `read_skill`

Check `--show-tools` output to confirm `read_skill` is actually present in
the deployed agent's tool list (it only appears when `skills=[...]` resolved
successfully at deploy time). If it's missing, redeploy with `--update`
after confirming `ncp validate .` reports all three skills.

### Authentication or deployment issues

```bash
ncp authenticate     # re-authenticate if credentials expired
ncp validate .        # check for structural issues first
ncp list               # confirm the agent actually deployed
```
