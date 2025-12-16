# Multi-Agent System

**Learn how to build multi-agent systems with AgentTool**

This example demonstrates how to create a multi-agent system where an orchestrator agent delegates tasks to specialized child agents. You'll learn how to wrap agents as tools and build hierarchical agent architectures.

---

## What You'll Learn

- **AgentTool**: How to wrap an Agent as a Tool
- **Multi-Agent Architecture**: Orchestrator pattern with specialized agents
- **Task Delegation**: How to route requests to appropriate specialists
- **Agent Composition**: Building complex systems from simple agents

---

## Quick Start

```bash
# Navigate to this example
cd multi-agent

# Install dependencies
pip install -r requirements.txt

# Validate the project
ncp validate .
```

---

## Project Structure

```
multi-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── agents/
│   ├── __init__.py
│   └── main_agent.py      # Orchestrator + child agents
└── tools/
    ├── __init__.py
    ├── math_tools.py       # Tools for math agent
    ├── research_tools.py   # Tools for research agent
    └── writing_tools.py    # Tools for writing agent
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                          │
│                                                              │
│  Analyzes request and delegates to specialists              │
│                                                              │
│  Tools: [math_expert, research_expert, writing_expert]      │
└─────────────┬───────────────┬───────────────┬───────────────┘
              │               │               │
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Math Agent    │ │ Research Agent  │ │  Writing Agent  │
│                 │ │                 │ │                 │
│ - calculate     │ │ - search        │ │ - format        │
│ - convert_units │ │ - summarize     │ │ - check_grammar │
│                 │ │                 │ │ - outline       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## How It Works

### Step 1: Define Specialized Agents

Create agents with focused capabilities:

```python
from ncp import Agent

math_agent = Agent(
    name="math_specialist",
    description="Expert at calculations and unit conversions",
    instructions="You are a math specialist...",
    tools=[calculate, convert_units],
)

research_agent = Agent(
    name="research_specialist",
    description="Expert at finding and summarizing information",
    instructions="You are a research specialist...",
    tools=[search_knowledge, summarize_topic],
)
```

### Step 2: Wrap Agents as Tools

Use `AgentTool` to make agents callable as tools:

```python
from ncp import AgentTool

math_tool = AgentTool(
    math_agent,
    name="math_expert",
    description="Delegate math problems to the math specialist"
)

research_tool = AgentTool(
    research_agent,
    name="research_expert",
    description="Delegate research questions to the research specialist"
)
```

### Step 3: Create the Orchestrator

Build an orchestrator that uses the agent tools:

```python
orchestrator = Agent(
    name="MultiAgentOrchestrator",
    description="Coordinates specialist agents",
    instructions="You coordinate a team of specialists...",
    tools=[math_tool, research_tool, writing_tool],
)
```

---

## AgentTool API

```python
from ncp import Agent, AgentTool

# Basic usage - name and description derived from agent
tool = AgentTool(agent)
# Result: name="agent_name_tool", description=agent.description

# Custom name and description
tool = AgentTool(
    agent,
    name="custom_name",
    description="Custom description for the tool"
)
```

### AgentTool Properties

| Property | Description |
|----------|-------------|
| `agent` | The wrapped Agent instance |
| `name` | Tool name (default: `{agent.name}_tool`) |
| `description` | Tool description (default: agent's description) |

### How Delegation Works

When the orchestrator calls an AgentTool:

1. A `query` parameter is passed to the child agent
2. Child agent runs with fresh context (no shared history)
3. Child agent uses its own tools to complete the task
4. Final response is returned to the orchestrator

---

## Example Interactions

### Math Delegation

```
You: What's 15% of $200?

Orchestrator: I'll delegate this to the math expert.
[Uses tool: math_expert(query="Calculate 15% of $200")]

Math Agent: Let me calculate that.
[Uses tool: calculate("200 * 0.15")]
15% of $200 is $30.00

Orchestrator: The math expert calculated that 15% of $200 is $30.00.
```

### Research Delegation

```
You: Tell me about machine learning

Orchestrator: I'll have the research expert help with this.
[Uses tool: research_expert(query="Explain machine learning")]

Research Agent: Let me search for information on this topic.
[Uses tool: search_knowledge("machine learning")]
[Uses tool: summarize_topic("machine learning")]

Machine learning is a subset of AI that enables systems to learn from data...

Orchestrator: Here's what the research expert found about machine learning...
```

### Multi-Expert Collaboration

```
You: Research cloud computing and create an outline for a report

Orchestrator: This needs both research and writing expertise.

[Uses tool: research_expert(query="Research cloud computing")]
Research Agent: [Provides cloud computing information]

[Uses tool: writing_expert(query="Create outline for cloud computing report")]
Writing Agent: [Generates document outline]

Orchestrator: Here's a comprehensive outline for your cloud computing report,
based on the research findings...
```

---

## Key Concepts

### Fresh Execution Context

Each AgentTool execution runs with fresh context:
- Child agent doesn't see parent's conversation history
- Only receives the query parameter
- Returns only the final response

This keeps child agents focused and prevents context pollution.

### Task Routing

The orchestrator's instructions guide task routing:

```python
instructions="""
Delegation guidelines:
- Math questions → math_expert
- Research questions → research_expert
- Writing tasks → writing_expert
- Complex requests may need multiple experts
"""
```

### Agent Independence

Each agent is independent and can be:
- Tested separately
- Deployed standalone
- Reused in different orchestrators

---

## When to Use Multi-Agent Systems

| Use Case | Benefit |
|----------|---------|
| Complex domains | Specialized agents for each domain |
| Large tool sets | Distribute tools across focused agents |
| Modular development | Build and test agents independently |
| Scalability | Add new specialists without changing others |

---

## Best Practices

1. **Keep agents focused**: Each agent should have a clear specialty
2. **Write clear descriptions**: The orchestrator uses these to route tasks
3. **Provide routing guidance**: Include delegation rules in orchestrator instructions
4. **Test agents independently**: Verify each agent works before composition
5. **Use meaningful names**: Make it clear what each agent does

---

## Next Steps

1. **Add more specialists**: Create agents for other domains
2. **Chain agents**: Have one agent's output feed into another
3. **Customize routing**: Fine-tune how the orchestrator delegates

```bash
# Package and deploy
ncp package .
ncp authenticate
ncp deploy multi-agent.ncp

# Test in playground
ncp playground --agent multi-agent
```
