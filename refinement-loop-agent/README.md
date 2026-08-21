# Refinement Loop Agent - Generator-Critic with `LoopAgent`

**Demonstrates `LoopAgent` + `StopCondition`: repeatedly revising a draft until a reviewer approves it.**

---

## 🎯 What This Example Teaches

1. **`LoopAgent`**: repeating a sequence of steps until a condition is met or the iteration cap is reached
2. **`StopCondition`**: declarative early-stopping — plain data, so it survives `ncp deploy` serialization
3. **Self-referential state**: how a step reads *its own* output from the previous pass, which is what makes refinement possible
4. **The generator-critic pattern**: one agent drafts, another judges, and the loop closes between them
5. **Why a presenter step comes after the loop**: so the final answer streams to the user

---

## 📁 Project Structure

```
refinement-loop-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 drafter + reviewer + loop + presenter
└── tools/
    ├── __init__.py
    └── change_tools.py     # 🔧 get_change_standards, review_change_plan
```

---

## 🔁 The Loop: `agents/main_agent.py`

```python
draft_change_plan = Agent(
    instructions="""...
Your previous draft, if you have made one, was:

{plan}

The reviewer's verdict on it was:

{review_status}
...""",
    tools=[get_change_standards],
    output_key="plan",              # ← read back by this same agent next pass
)

review_plan = Agent(
    instructions="...reply with exactly `approved` or `needs_revision` + problems...",
    tools=[review_change_plan],
    output_key="review_status",     # ← what the stop condition watches
)

refinement_loop = LoopAgent(
    sub_agents=[draft_change_plan, review_plan],
    max_iterations=4,
    stop_on=StopCondition(state_key="review_status", equals="approved"),
    share_state=True,
)
```

```
      ┌────────────────────────────────────────────┐
      │ draft_change_plan  ──▶ state["plan"]        │
      │ review_plan        ──▶ state["review_status"]│
      └───────── repeat while != "approved" ────────┘
                          ↓
                 present_change_plan
```

### Self-referential state — the bit that makes refinement work

On pass 2, the drafter must see the draft **it** produced on pass 1, plus what
the reviewer objected to. A step can **always** read its own `output_key` from
the previous iteration — that holds even with `share_state=False`, because a
step reading its own prior output isn't "seeing unrelated history", it's the
entire basis of iterative refinement.

`share_state=True` is set here for a *different* reason: so the drafter can also
read `{review_status}`, which belongs to the reviewer. Reading its own `{plan}`
needs no flag.

### Why `StopCondition` is data, not a function

```python
stop_on = StopCondition(state_key="review_status", equals="approved")
```

A callable would be more flexible, but it couldn't be serialized — and every
field of a deployed agent has to survive `ncp package` / `ncp deploy`. Keeping
it declarative means the loop behaves identically locally and on the platform.

`max_iterations=4` bounds the loop regardless: a plan the reviewer keeps
rejecting stops after four passes rather than spinning.

### Why there's a presenter step after the loop

A `LoopAgent` **can't stream its answer**. Whether a pass is the last one is only
known *after* the stop condition is evaluated, and chat output is append-only —
so streaming every pass would stack all the drafts on top of each other in the
user's chat bubble.

Wrapping the loop in a `SequentialAgent` with a presenter step after it fixes
this: the presenter is the last step, so it becomes the workflow's answer and
streams normally, token by token.

```python
change_planning_workflow = SequentialAgent(
    sub_agents=[refinement_loop, present_change_plan],
)
```

This is the general recipe whenever a loop's result is what the user should see.

---

## 🚀 Try It Out

```bash
cd refinement-loop-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy refinement-loop-agent.ncp
ncp playground --agent change_planner --show-tools
```

### Example 1: A plan that needs revising

**You**: I need to upgrade firmware on all our access switches

**Agent**: The first draft targets everything at once and omits a rollback, so
`review_change_plan` returns `needs_revision`. The loop runs again; the drafter
stages the rollout (canary → one site → the rest) and adds a rollback procedure.
The reviewer returns `approved`, the loop stops early — well before its 4-pass
cap — and the presenter streams the approved plan.

### Example 2: Just the rules

**You**: What are our change-management standards?

**Agent**: calls `get_change_standards` and answers directly — no loop.

---

## 🎓 Key Takeaways

- A step can always read **its own** `output_key` from the previous pass; `share_state=True` is only needed to read *other* steps' outputs
- `StopCondition` stays declarative so it survives deployment — pair it with `max_iterations` as a backstop
- The critic's job is to emit a **machine-checkable verdict**; keep that value simple and exact, since the stop condition compares it literally
- Put a **presenter step after the loop** whenever the user should see the refined result streamed

## 🚀 Next Steps

- Add a third loop step that estimates blast radius, and stop only when it's below a threshold
- Have the reviewer hand off to a human approver for MAJOR changes (see `handoff-agent`)
- Feed the approved plan into a fan-out that opens one ticket per affected site (see `dynamic-fanout-agent`)
