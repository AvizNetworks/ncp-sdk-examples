# Routing Agent - One-Shot Triage with `RoutingAgent`

**Demonstrates `RoutingAgent`: classify the request once, up front, then hand it entirely to one specialist.**

---

## 🎯 What This Example Teaches

1. **`RoutingAgent`**: classify-then-delegate, decided before any specialist starts
2. **`router` vs. `routes`**: the router emits a *label*, never an answer; the matched route produces the whole response
3. **`default_route`**: surviving an unexpected classifier output instead of failing the request
4. **Choosing between the three delegation patterns**: routing vs. `handoff()` vs. an `AgentTool` orchestrator

---

## 📁 Project Structure

```
routing-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py       # 🎯 classifier + 3 specialists + the router
└── tools/
    ├── __init__.py
    └── support_tools.py    # 🔧 look_up_invoice, search_kb
```

---

## 🔀 The Router: `agents/main_agent.py`

```python
classifier = Agent(
    name="classifier",
    instructions="""...reply with EXACTLY ONE of these words, lowercase:
billing / technical / general ...""",
)

support_router = RoutingAgent(
    name="support_router",
    router=classifier,
    routes={
        "billing":   billing_agent,
        "technical": technical_agent,
        "general":   general_agent,
    },
    default_route="general",
)
```

```
"Is invoice ACME-2291 still outstanding?"
              ↓
         classifier  ──▶  "billing"
              ↓
        billing_agent  ──▶  the answer the user sees
```

### The router never talks to the user

Its output is a route label — `"billing"` — not prose. That word is consumed to
pick a branch and is never streamed to the user; only the matched specialist's
answer is. Matching is whitespace- and case-insensitive, so a classifier that
replies `" Billing\n"` still lands correctly.

The specialist then runs against the **original** user request, not the label —
the router classifies, it never rewrites what was asked.

### `default_route` is a safety net

Classifiers occasionally return something unexpected. With `default_route="general"`
that becomes a graceful fallback; **without** one, an unmatched label is a hard
error. Set it whenever the request failing outright would be worse than being
handled by a generalist.

---

## 🧭 Routing vs. Handoff vs. Orchestrator

Three patterns in this repo pick a specialist. They are not interchangeable:

| Pattern | When the decision is made | Who answers the user | Example |
|---|---|---|---|
| **`RoutingAgent`** | **Once, before** any specialist starts | Exactly one specialist | this example |
| **`handoff()`** | **Mid-conversation**, after the first agent has begun | The target, continuing the same conversation with shared history | `handoff-agent` |
| **`AgentTool` orchestrator** | **Continuously** — the parent LLM decides each turn | The parent, composing specialists' results | `multi-agent` |

Rule of thumb:

- **Routing** — triage, where one specialist owns the whole answer
- **Handoff** — escalation, where a conversation already underway needs to change owner
- **Orchestrator** — composition, where the answer needs several specialists combined

---

## 🚀 Try It Out

```bash
cd routing-agent
pip install -r requirements.txt
ncp validate .
ncp package .
ncp deploy routing-agent.ncp
ncp playground --agent support_desk --show-tools
```

### Example 1: Billing

**You**: Is invoice ACME-2291 still outstanding?

**Agent**: classifier → `billing` → `billing_agent` calls `look_up_invoice` and
reports $18,400.00, overdue by 12 days. You never see the word "billing" — only
the answer.

### Example 2: Technical

**You**: Our site-to-site VPN keeps dropping every few minutes

**Agent**: classifier → `technical` → `technical_agent` calls `search_kb("vpn")`
and walks through the lifetime-mismatch, PSK-rotation, and NAT-T checks.

### Example 3: General

**You**: Who do I contact to add a user to our account?

**Agent**: classifier → `general` → `general_agent` answers and points at the
right team.

---

## 🎓 Key Takeaways

- The router's output is a **label**, not an answer — keep its instructions blunt about emitting one bare word
- Route keys and classifier output are matched case- and whitespace-insensitively
- The chosen specialist sees the **original** request, not the label
- Set `default_route` unless an unroutable request genuinely should fail
- Reach for `handoff()` instead when the conversation is already underway, or an orchestrator when one specialist won't be enough

## 🚀 Next Steps

- Add a fourth route (e.g. `security`) — just one more `routes` entry and one line in the classifier's instructions
- Make a route a whole pipeline rather than a single agent (see `sequential-pipeline-agent`) — routes accept any workflow node
- Let `technical_agent` escalate urgent outages via `handoff()` (see `handoff-agent`)
