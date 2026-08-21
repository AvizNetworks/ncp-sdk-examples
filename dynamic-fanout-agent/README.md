# Dynamic Fan-Out Agent - Runtime-Sized Concurrency with `DynamicParallelAgent`

**Demonstrates `DynamicParallelAgent`: a fan-out whose number of branches is decided while the workflow runs, not when it's written.**

---

## 🎯 What This Example Teaches

1. **`DynamicParallelAgent`**: replicating one template agent once per item in a runtime-determined list
2. **`items_from_state`**: reading the branch list from a key an earlier step wrote
3. **`max_concurrency`**: capping how many branches run at once, however many were planned
4. **Planner → fan-out → aggregate**: the standard shape for "figure out the work, then do all of it"
5. **When to use this vs. `ParallelAgent`**: fixed branches vs. branches that depend on the request

---

## 📁 Project Structure

```
dynamic-fanout-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 planner + template + fan-out + aggregator
└── tools/
    ├── __init__.py
    └── audit_tools.py      # 🔧 list_sites, audit_site
```

---

## 📐 Fixed vs. Runtime-Sized Fan-Out

`parallel-fanout-agent` hardcodes its branches — three regions, three
`AgentInvocation` entries, decided when the workflow was written:

```python
ParallelAgent(sub_agents=[
    AgentInvocation(agent=region_health_agent, query="...us-east",    output_key="us_east_health"),
    AgentInvocation(agent=region_health_agent, query="...us-west",    output_key="us_west_health"),
    AgentInvocation(agent=region_health_agent, query="...eu-central", output_key="eu_central_health"),
])
```

That's right when you always check the same things. It can't express *"audit
every datacenter"* or *"audit the branch sites"*, where the branch count depends
on what was asked. `DynamicParallelAgent` sizes itself instead:

```python
plan_audit_scope = Agent(
    instructions="...Respond with ONLY a JSON array of site name strings...",
    tools=[list_sites],
    output_key="audit_scope",          # ← writes e.g. ["dc-east", "dc-west", "dc-fra"]
)

audit_all_planned_sites = DynamicParallelAgent(
    template=site_auditor,             # ← replicated once per item
    items_from_state="audit_scope",    # ← reads the planner's list
    item_output_key_prefix="site_audit",
    max_concurrency=3,
)

site_audit_workflow = SequentialAgent(
    sub_agents=[plan_audit_scope, audit_all_planned_sites, summarize_audit],
)
```

```
"audit the datacenters"
        ↓
plan_audit_scope  ──▶  ["dc-east", "dc-west", "dc-fra"]
        ↓
DynamicParallelAgent  ─┬─▶ site_auditor("dc-east")  ──┐
                       ├─▶ site_auditor("dc-west")  ──┼─▶ merged findings
                       └─▶ site_auditor("dc-fra")   ──┘
        ↓
summarize_audit  ──▶  one compliance report
```

Ask for the branches instead and you get two. Ask for everything and you get
six. Same code.

### Two things worth knowing

**`items_from_state` doesn't need `share_state`.** Wiring `items_from_state` is
an explicit structural read you set up on purpose — unlike implicit
`{placeholder}` templating, it always sees the workflow's state. But the planner
and the fan-out **must be steps of the same pipeline**: that's what lets the
fan-out see what the planner just wrote.

**Malformed planner output fails loudly.** The planner's list is LLM output
crossing a real boundary, so if it isn't valid JSON, or isn't a list of strings,
the workflow raises rather than quietly fanning out to nothing. That's why the
planner's instructions are so blunt about emitting *only* a JSON array.

**`max_concurrency=3`** caps simultaneous branches — the planner may select six
sites, but only three are audited at a time, which keeps the backing systems from
being hammered.

---

## 🚀 Try It Out

```bash
cd dynamic-fanout-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy dynamic-fanout-agent.ncp
ncp playground --agent compliance_auditor --show-tools
```

### Example 1: Scope decided from a tier

**You**: Audit all our datacenters

**Agent**: the planner resolves that to `["dc-east", "dc-west", "dc-fra"]`, three
branches run concurrently, and the report leads with `dc-fra` (MAJOR —
unrestricted VTY access lists, unauthenticated NTP).

### Example 2: A different scope, same code

**You**: Audit the branch offices

**Agent**: the planner resolves `["branch-nyc", "branch-sfo"]` — two branches this
time. `branch-sfo` flags a default SNMP community string.

### Example 3: No fan-out

**You**: What sites do you know about?

**Agent**: calls `list_sites` and answers directly.

---

## 🎓 Key Takeaways

- Use `ParallelAgent` when you know the branches up front; `DynamicParallelAgent` when an earlier step decides them
- The planner must emit **strict JSON** — say so bluntly in its instructions, because malformed output is a hard error, not a silent no-op
- The planner and fan-out must be steps of the **same** pipeline for `items_from_state` to resolve
- `max_concurrency` decouples "how much work was planned" from "how much runs at once"

## 🚀 Next Steps

- Add a severity filter so the planner only selects sites that failed their last audit
- Chain a second `DynamicParallelAgent` that opens a remediation ticket per MAJOR finding
- Have the aggregator hand off to a specialist when it finds a MAJOR issue (see `handoff-agent`)
