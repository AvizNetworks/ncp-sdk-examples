# file-agent

An NCP AI agent project.

## Project Structure

```
file-agent/
├── ncp.toml              # Project configuration
├── requirements.txt      # Python dependencies
├── apt-requirements.txt  # System dependencies (optional)
├── agents/               # Agent definitions
│   └── main_agent.py    # Main agent entry point
└── tools/                # Custom tools (optional)
    └── __init__.py
```

## Quick Start

### 1. Authenticate with Platform

First, authenticate with your NCP platform:

```bash
ncp authenticate
```

You'll be prompted for:

- Platform URL (e.g., `https://ncp.example.com`)
- Username
- Password

Credentials are saved to `ncp.toml` for future commands.

### 2. Validate Project

Validate your agent configuration:

```bash
ncp validate .
```

This checks:

- `ncp.toml` syntax and structure
- Agent definitions and imports
- Tool implementations
- Dependencies

### 3. Package Agent

Create a deployment package:

```bash
ncp package .
```

Creates `file-agent.ncp` containing all agent files and dependencies.

### 4. Deploy Agent

Deploy to the platform:

```bash
# First deployment
ncp deploy file-agent.ncp

# Update existing agent
ncp deploy file-agent.ncp --update
```

The `--update` flag automatically extracts the agent name from the package.

### 5. Test in Playground

Test your agent interactively:

```bash
ncp playground --agent file-agent

# Show tool calls and results
ncp playground --agent file-agent --show-tools
```

Exit playground with `Ctrl+C`.

## Managing Agents

### List Deployed Agents

View all your deployed agents:

```bash
ncp list
```

Shows a table with agent names, versions, and deployment dates.

### Remove Agent

Remove an agent from the platform:

```bash
ncp remove --agent file-agent
```

You'll be prompted to confirm before removal.

## Development Workflow

### Typical Development Cycle

1. **Make changes** to your agent code
2. **Validate** - `ncp validate .`
3. **Package** - `ncp package .`
4. **Deploy/Update** - `ncp deploy file-agent.ncp --update`
5. **Test** - `ncp playground --agent file-agent`
6. **Iterate** - Repeat steps 1-5

### Adding Custom Tools

Create tools in your agent file or in `tools/`. This project includes example weather tools:

```python
from ncp import tool

@tool
def get_current_weather(location: str) -> dict:
    """Get current weather conditions for a location.

    Args:
        location: City name or location

    Returns:
        Dictionary containing current weather information
    """
    # Your implementation here
    return {"temperature": 22, "condition": "sunny"}
```

Then add to your agent:

```python
from ncp import Agent
from tools import get_current_weather, get_weather_forecast

agent = Agent(
    name="WeatherAgent",
    description="Weather information assistant",
    instructions="You help users get weather information",
    tools=[get_current_weather, get_weather_forecast],
)
```

### Using MCP Servers

Add external tools via MCP servers:

```python
from ncp import Agent, MCPConfig

agent = Agent(
    name="file-agent",
    description="Agent with MCP tools",
    instructions="Your instructions",
    mcp_servers=[
        MCPConfig(
            command="mcp-server-fetch",
            transport_type="stdio"
        )
    ]
)
```

### Customizing LLM Configuration (Optional)

The platform uses default LLM settings, but you can customize generation parameters if needed:

```python
from ncp import Agent, LLMConfig

agent = Agent(
    name="file-agent",
    description="Your agent",
    instructions="Your instructions",
    llm_config=LLMConfig(
        temperature=0.7,      # 0.0-2.0, default: 0.7
        max_tokens=2000,      # Optional, limits response length
    )
)
```

**Note:** The model, API key, and base URL are managed by the platform. Only customize `llm_config` if you need different generation parameters than the defaults.

## Configuration Files

### ncp.toml

Main project configuration:

```toml
[project]
name = "file-agent"
version = "0.1.0"
description = "Your agent description"

[agents]
main = "agents.main_agent:agent"

[build]
python_version = "3.11"
```

### requirements.txt

Python dependencies (installed automatically during deployment):

```
# Add your Python package dependencies here
# Example:
# requests>=2.31.0
# pandas>=2.0.0
```

### apt-requirements.txt (Optional)

System packages (installed automatically during deployment):

```
# Add system dependencies here
# Example:
# ffmpeg
# poppler-utils
```

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate if credentials expire
ncp authenticate
```

### Deployment Failures

```bash
# Check validation first
ncp validate .

# View deployed agents
ncp list
```

### Platform Connection Issues

Verify the platform URL in `ncp.toml` under `[platform]` section.
