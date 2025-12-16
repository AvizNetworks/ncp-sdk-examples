# Memory Config Agent

**Learn how to configure memory strategies for conversation management**

This example demonstrates how to configure different memory strategies that control how much conversation history your agent retains. You'll learn about TOKEN_WINDOW and LAST_N_MESSAGES strategies.

---

## What You'll Learn

- **TOKEN_WINDOW Strategy**: Token-budget based context management (default)
- **LAST_N_MESSAGES Strategy**: Fixed message count based context
- **Stateless Mode**: Disable memory for single-turn interactions
- **Configuration Options**: Fine-tune memory behavior for your use case

---

## Quick Start

```bash
# Navigate to this example
cd memory-config-agent

# Install dependencies
pip install -r requirements.txt

# Validate the project
ncp validate .
```

---

## Project Structure

```
memory-config-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py      # Agent with memory configuration
└── tools/
    ├── __init__.py
    └── conversation_tools.py
```

---

## Memory Strategies

### 1. TOKEN_WINDOW (Default)

Best for long conversations where you want to maximize context usage.

```python
from ncp import MemoryConfig, STMStrategy

config = MemoryConfig(
    stm_enabled=True,
    stm_strategy=STMStrategy.TOKEN_WINDOW,
    stm_config={
        "max_context_tokens": 131072,  # 128K context window
        "generation_buffer": 0.25,      # Reserve 25% for output
        "tool_tokens": 0,               # Managed automatically
    }
)
```

**How it works:**
- Calculates available tokens: `max_context_tokens * (1 - generation_buffer) - tool_tokens`
- Keeps as many conversation turns as fit within this budget
- Always preserves: system message + current user message
- Fills remaining space with recent history, newest first

**Configuration:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_context_tokens` | 131072 | Model's context window size |
| `generation_buffer` | 0.25 | Fraction reserved for model output (0.1-0.5) |
| `tool_tokens` | 0 | Reserved for tool schemas (auto-managed) |

### 2. LAST_N_MESSAGES

Best for predictable context size and simpler memory management.

```python
config = MemoryConfig(
    stm_enabled=True,
    stm_strategy=STMStrategy.LAST_N_MESSAGES,
    stm_config={
        "max_messages": 20,      # Keep last 20 turns
        "include_tools": True,   # Include tool calls in context
    }
)
```

**How it works:**
- Keeps the last N conversation "turns"
- A turn = user message + tool calls + tool results + assistant response
- Simple and predictable behavior

**Configuration:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_messages` | 20 | Number of conversation turns to keep |
| `include_tools` | True | Include tool calls and results in context |

### 3. Stateless Mode

For single-turn interactions with no conversation history.

```python
config = MemoryConfig(stm_enabled=False)
```

**How it works:**
- Each request is independent
- Only system message + current user message sent to LLM
- Best for: stateless APIs, one-shot queries

---

## Usage Examples

### Default Configuration (TOKEN_WINDOW)

```python
from ncp import Agent, MemoryConfig

# Uses TOKEN_WINDOW with 128K context by default
agent = Agent(
    name="MyAgent",
    description="An agent with default memory",
    instructions="You are a helpful assistant.",
    tools=[...],
    memory_config=MemoryConfig()  # Default settings
)
```

### Smaller Context Window

For cost-effective shorter conversations:

```python
config = MemoryConfig(
    stm_config={
        "max_context_tokens": 32768,  # 32K instead of 128K
        "generation_buffer": 0.30,     # 30% for generation
    }
)
```

### Message-Based Memory

For predictable turn counts:

```python
config = MemoryConfig(
    stm_strategy=STMStrategy.LAST_N_MESSAGES,
    stm_config={
        "max_messages": 10,      # Keep last 10 turns
        "include_tools": False,  # Exclude tool calls (save tokens)
    }
)
```

---

## Example Interaction

```
You: Hi! My name is Alex and I work in software engineering.

Agent: Nice to meet you, Alex! I've noted that you work in software engineering.
[Uses tool: remember_fact("name", "Alex")]
[Uses tool: remember_fact("profession", "software engineering")]

You: What do you remember about me?

Agent: Based on our conversation, I remember that:
- Your name is Alex
- You work in software engineering

You: I also love hiking on weekends.

Agent: Great to know! I've added that to what I know about you.
[Uses tool: remember_fact("hobby", "hiking on weekends")]

You: Can you summarize what we've discussed?

Agent: Of course! Here's a summary of our conversation:
[Uses tool: get_current_context("user information")]

We've discussed several things about you:
1. Your name is Alex
2. You work in software engineering
3. You enjoy hiking on weekends

Is there anything else you'd like me to remember or discuss?
```

---

## Key Concepts

### System Message Preservation

The system message (agent instructions) is **always preserved** regardless of memory configuration. This ensures the agent maintains its core behavior.

### Turn-Based Memory

Both strategies use the concept of "turns":
- **User message** starts a new turn
- **Tool calls** and **tool results** are part of the turn
- **Assistant response** completes the turn

### Memory vs. Persistence

- **Memory (STM)**: What the agent remembers within a conversation session
- **Persistence**: Handled by the platform via `conversation_id`

The SDK configures memory behavior; the platform handles persistence across sessions.

---

## When to Use Each Strategy

| Use Case | Recommended Strategy |
|----------|---------------------|
| Long technical discussions | TOKEN_WINDOW (large context) |
| Customer support chats | LAST_N_MESSAGES (20 turns) |
| Quick Q&A | TOKEN_WINDOW (small context) or Stateless |
| API integrations | Stateless |
| Cost-sensitive applications | LAST_N_MESSAGES or small TOKEN_WINDOW |

---

## Next Steps

1. **Experiment**: Change `memory_config` in `main_agent.py` and observe behavior
2. **Deploy**: Package and deploy to test with real conversations
3. **Tune**: Adjust parameters based on your conversation patterns

```bash
# Package and deploy
ncp package .
ncp authenticate
ncp deploy memory-config-agent.ncp

# Test in playground
ncp playground --agent memory-config-agent
```
