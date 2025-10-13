# Weather Agent

**Learn how to use MCP (Model Context Protocol) servers for external capabilities**

This example demonstrates how to integrate external MCP servers into your agents, allowing you to use pre-built tools without writing custom Python code. You'll learn how MCP servers provide powerful capabilities like HTTP fetching, and how agents can leverage them.

---

## 🎯 What You'll Learn

By the end of this example, you'll understand:

- ✅ **MCP Integration**: How to configure and use external MCP servers
- ✅ **No Custom Tools**: How agents can work without writing Python tool functions
- ✅ **Tool Discovery**: How MCP servers expose tools automatically
- ✅ **External APIs**: How to fetch data from web services
- ✅ **Real-World Data**: Working with live weather information
- ✅ **MCPConfig**: Configuring MCP servers with command, args, and env

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- NCP SDK installed (`pip install ncp-sdk`)
- Completed [hello-agent](../hello-agent) and [calculator-agent](../calculator-agent) (recommended)

### Installation

```bash
# Navigate to this example
cd weather-agent

# Install dependencies (including mcp-server-fetch)
pip install -r requirements.txt

# Validate the project
ncp validate .
```

---

## 📁 Project Structure

```
weather-agent/
├── README.md              # This file - tutorial and guide
├── ncp.toml              # Project configuration
├── requirements.txt      # Python dependencies (includes MCP server)
└── agents/
    ├── __init__.py
    └── main_agent.py    # Agent with MCP configuration
```

**Note**: No `tools/` directory! This agent uses MCP tools instead of custom Python tools.

---

## 🔧 What is MCP?

**MCP (Model Context Protocol)** is a standard for connecting AI agents to external tool servers.

### Why MCP?

Instead of writing custom Python tools for every capability, you can:

1. **Use pre-built MCP servers** maintained by the community
2. **Connect to existing services** without writing integration code
3. **Add capabilities instantly** by configuring a server
4. **Keep agents lightweight** - tools run in separate processes

### MCP Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Agent     │ ─────>  │ MCP Protocol │ ─────>  │  MCP Server  │
│             │  calls  │              │  stdio  │  (fetch)     │
└─────────────┘         └──────────────┘         └──────────────┘
                                                         │
                                                         ▼
                                                  ┌──────────────┐
                                                  │  Web APIs    │
                                                  │  (wttr.in)   │
                                                  └──────────────┘
```

---

## 🌦️ The MCP Server: mcp-server-fetch

This agent uses **mcp-server-fetch**, which provides:

### Tool: `fetch`

Makes HTTP requests to any URL and returns the response.

**Parameters**:

- `url` (string): The URL to fetch
- `method` (string, optional): HTTP method (GET, POST, etc.) - default: GET
- `headers` (object, optional): HTTP headers
- `body` (string, optional): Request body for POST/PUT

**Returns**: HTTP response with status, headers, and body

### Example Usage in Agent

The agent can call:

```python
fetch(url="https://wttr.in/London?format=j1")
```

And receive weather data in JSON format!

---

## 🎬 Example Interactions

### Basic Weather Query

```
You: What's the weather in London?

Agent: Let me check the current weather in London.
[Uses MCP tool: fetch(url="https://wttr.in/London?format=j1")]

The weather in London is currently:
- Temperature: 15°C (59°F)
- Conditions: Partly cloudy
- Feels like: 13°C
- Humidity: 72%
- Wind: 15 km/h SW
- Visibility: 10 km

It's a pleasant day with some clouds!
```

### Multiple Cities

```
You: Compare the weather in Tokyo and New York

Agent: I'll get the weather for both cities.

[Uses MCP tool: fetch(url="https://wttr.in/Tokyo?format=j1")]
[Uses MCP tool: fetch(url="https://wttr.in/New York?format=j1")]

Here's the weather comparison:

Tokyo:
- Temperature: 22°C (72°F) ☀️
- Conditions: Sunny
- Humidity: 55%

New York:
- Temperature: 18°C (64°F) ⛅
- Conditions: Partly cloudy
- Humidity: 68%

Tokyo is warmer and sunnier right now!
```

### Error Handling

```
You: What's the weather in Atlantis?

Agent: Let me check...
[Uses MCP tool: fetch(url="https://wttr.in/Atlantis?format=j1")]

I couldn't find weather information for "Atlantis".
This might be because the city name isn't recognized or doesn't exist.

Could you check the spelling, or try a nearby major city?
```

---

## 💡 The "Aha!" Moment

Ask it: **"What should I wear in San Francisco today?"**

Watch the agent:

1. **Fetch weather data** using the MCP server
2. **Parse the response** to understand conditions
3. **Reason about temperature and conditions**
4. **Provide practical advice** based on the data

The agent combines **external data** (via MCP) with **AI reasoning** to give helpful recommendations!

---

## 🧠 Key Concepts

### 1. MCP Configuration

The agent configures the MCP server using `MCPConfig`:

```python
from ncp import MCPConfig

agent = Agent(
    name="WeatherAgent",
    mcp_servers=[
        MCPConfig(
            command="mcp-server-fetch",  # Command to run
            args=[],                      # Command arguments
            env=None,                     # Environment variables
        )
    ]
)
```

**How it works**:

1. NCP SDK spawns `mcp-server-fetch` as a subprocess
2. Communicates via stdio (standard input/output)
3. Server exposes available tools (like `fetch`)
4. Agent can call these tools like Python functions

### 2. No Custom Tools Needed

Notice `tools=[]` in the agent definition:

```python
agent = Agent(
    name="WeatherAgent",
    tools=[],  # Empty! Using MCP tools instead
    mcp_servers=[MCPConfig(...)]
)
```

The agent has capabilities without Python code - the MCP server provides them!

### 3. Tool Discovery

When the agent starts:

1. NCP SDK connects to the MCP server
2. Server sends list of available tools
3. Tools are added to the agent automatically
4. LLM can now call `fetch` like any other tool

### 4. Instructions Guide MCP Usage

The agent's instructions explain **how to use** the MCP tool:

```python
instructions="""...
To get weather information:
1. Use the fetch tool to call: https://wttr.in/{city}?format=j1
2. Parse the JSON response to extract weather data
3. Present information in a friendly way
..."""
```

**This is crucial!** The LLM needs to know:

- Which tool to use (`fetch`)
- How to use it (URL format, parameters)
- What to do with the result (parse, present)

---

## 📚 Code Deep Dive

### Agent Definition

```python
from ncp import Agent
from ncp import MCPConfig

agent = Agent(
    name="WeatherAgent",
    description="A weather assistant that fetches real-time weather information using MCP",
    instructions="""[Detailed instructions on using the fetch tool]...""",
    tools=[],  # No Python tools
    mcp_servers=[
        MCPConfig(
            command="mcp-server-fetch",
            args=[],
            env=None,
        )
    ],
)
```

**Key Points**:

- `tools=[]` - No custom Python functions needed
- `mcp_servers=[...]` - List of MCP servers to connect to
- `MCPConfig` - Configuration for each server

### MCPConfig Parameters

```python
MCPConfig(
    command="mcp-server-fetch",  # Executable name (must be in PATH or absolute path)
    args=[],                      # Command-line arguments (list of strings)
    env=None,                     # Environment variables (dict or None)
)
```

**Additional options** (not used in this example):

- `cwd` - Working directory for the process
- `timeout` - Connection timeout in seconds

---

## 🔬 Try It Yourself

### Experiment 1: Different Cities

```
- "What's the weather in Paris?"
- "Tell me about the weather in Mumbai"
- "How's the weather in Sydney, Australia?"
```

### Experiment 2: Weather Comparisons

```
- "Compare weather in Miami and Seattle"
- "Which is warmer: Cairo or Dubai?"
- "Is it raining in London or Manchester?"
```

### Experiment 3: Contextual Questions

```
- "Should I bring an umbrella in Boston today?"
- "What should I wear in Chicago right now?"
- "Is it good beach weather in Barcelona?"
```

### Experiment 4: Invalid Queries

```
- "Weather in XYZ123"
- "What's the weather on Mars?"
```

See how the agent handles errors gracefully!

## 🚀 Next Steps

### Modify This Agent

Try these extensions:

1. **Add more MCP servers**:

   ```python
   mcp_servers=[
       MCPConfig(command="mcp-server-fetch", args=[]),
       MCPConfig(command="mcp-server-time", args=[]),  # Add time tools
   ]
   ```

2. **Use different APIs**:
   - Currency exchange rates
   - Stock prices
   - News headlines
   - GitHub repository info

3. **Enhance instructions**:
   - Add forecast lookups (wttr.in supports multi-day)
   - Include sunrise/sunset times
   - Suggest activities based on weather

### Other MCP Servers to Try

Popular MCP servers you can integrate:

- **mcp-server-filesystem** - File operations
- **mcp-server-postgres** - Database queries
- **mcp-server-git** - Git operations
- **mcp-server-slack** - Slack integration
- **mcp-server-github** - GitHub API

Install with pip and configure with `MCPConfig`!

### Deploy It

```bash
# Package the agent
ncp package .

# Authenticate with platform
ncp authenticate

# Deploy
ncp deploy weather-agent.ncp

# Test in playground
ncp playground --agent weather-agent
```
