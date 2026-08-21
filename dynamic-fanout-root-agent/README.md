# Dynamic Fanout Root Agent - Deploying a Runtime-Sized Fan-Out's `SequentialAgent` as the Entry Point

**Demonstrates deploying the *enclosing* `SequentialAgent` of a `DynamicParallelAgent` fan-out as the entry point itself - and why the `DynamicParallelAgent` step can never stand alone, root or not.**

---

## 🎯 What This Example Teaches

1. **The general root mechanism, applied again.** Same as `sequential-pipeline-root-agent`: `ncp.toml`'s `entry_point` names a workflow composition node directly, skipping the wrapping `Agent`/`AgentTool`.
2. **A `DynamicParallelAgent`-specific rule, stronger than `ParallelAgent`'s.** `parallel-fanout-root-agent` couldn't deploy a bare `ParallelAgent` as root because its output isn't prose. A `DynamicParallelAgent` can't even get that far: it structurally depends on an earlier sibling step, so it cannot run as *any* kind of standalone node - nested or root.
3. **What "root" means here, concretely.** The entry point is `site_audit_workflow` - the three-step `SequentialAgent` that already contains the planner, the fan-out, and the summarizer - not `audit_all_planned_sites` on its own.

---

## 📁 Project Structure

```
dynamic-fanout-root-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py           # 🎯 planner + template + fan-out + summarizer - no wrapping Agent
└── tools/
    ├── __init__.py
    └── audit_tools.py           # 🔧 list_sites, audit_site
```

---

## 🔗 The Pipeline: `agents/main_agent.py`

```python
from ncp import Agent, DynamicParallelAgent, SequentialAgent

plan_audit_scope = Agent(..., tools=[list_sites], output_key="audit_scope")
site_auditor      = Agent(..., tools=[audit_site])

audit_all_planned_sites = DynamicParallelAgent(
    template=site_auditor,
    items_from_state="audit_scope",
    item_output_key_prefix="site_audit",
    max_concurrency=3,
)

summarize_audit = Agent(..., instructions="...aggregate per-site audits into one report...")

site_audit_workflow = SequentialAgent(
    sub_agents=[plan_audit_scope, audit_all_planned_sites, summarize_audit],
)
```

This is unchanged from `dynamic-fanout-agent` - see that example's README for
how the planner sizes the fan-out at runtime via `items_from_state`. What's
different here is what deploys, and why it has to be `site_audit_workflow`
rather than `audit_all_planned_sites`.

### Why the entry point can't be the bare `DynamicParallelAgent`

```toml
# ncp.toml
[build]
entry_point = "agents.main_agent:site_audit_workflow"
```

`DynamicParallelAgent.items_from_state` reads a state key that an *earlier
sibling step in the same pipeline* wrote - here, `plan_audit_scope`'s JSON
list of site names. That dependency is structural, not stylistic: a
`DynamicParallelAgent` has no input of its own to size itself from except
"whatever an earlier step already put in this pipeline's state." Running it
as the outermost node would mean there is no earlier sibling, and therefore
nothing to read - the SDK's own workflow module documents this explicitly as
a hard constraint, not a recommendation.

This makes `DynamicParallelAgent` stricter than `ParallelAgent`
(`parallel-fanout-root-agent`), which *can* run standalone - it just produces
a merged dict that still needs a synthesis step to become an answer.
`DynamicParallelAgent` cannot run standalone in the first place.

> **Try it:** ask this agent to audit "the datacenters." You'll see
> `plan_audit_scope` announced, then `audit_all_planned_sites` fan out to
> however many sites matched (here: three), then `summarize_audit` streams
> back the compliance report - exactly as it would if this same
> `site_audit_workflow` were deployed wrapped behind a plain `Agent` instead.

---

## 🚀 Try It Out

```bash
cd dynamic-fanout-root-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy dynamic-fanout-root-agent.ncp
ncp playground --agent site_audit_workflow --show-tools
```

### Example: Running the audit

**You**: Audit the datacenters

**Agent**: `plan_audit_scope` reads `list_sites` and picks the three
datacenter-tier sites; `audit_all_planned_sites` audits all three
concurrently; `summarize_audit` streams back one compliance report.

### Example: A different scope, same pipeline

**You**: Audit everything

**Agent**: same three steps, but the fan-out now sizes itself to all six
sites - no code change, because the branch count was never fixed in the first
place.

---

## 🎓 Key Takeaways

- `ncp.toml`'s `entry_point` can name any workflow composition node, including one nested inside another - what matters is that the *outermost* node is one the platform can actually run standalone
- A `DynamicParallelAgent` can never be a deployment root, or any kind of standalone node - it structurally depends on an earlier sibling step having already run
- This is a stricter version of `parallel-fanout-root-agent`'s rule: a `ParallelAgent` can stand alone (just not usefully as a root), a `DynamicParallelAgent` cannot stand alone at all

## 🚀 Next Steps

- Compare with `parallel-fanout-root-agent`, where the constraint is softer - `ParallelAgent` can run standalone, it just isn't a good root
- Compare with `refinement-loop-root-agent`, where the constraint is about *streaming*, not standalone execution - a `LoopAgent` can run standalone just fine, it simply can't be the one step whose text reaches the user
