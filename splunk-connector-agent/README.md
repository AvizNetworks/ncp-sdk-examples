# Splunk Connector Agent


## 🎯 What You'll Learn

- **NCP Connectors**: How to use pre-configured platform connectors vs. manual MCP setup
- **Splunk Integration**: Searching with SPL (Splunk Processing Language)
- **SPL Query Construction**: Building effective searches for network operations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- NCP SDK installed (`pip install ncp-sdk`)
- **Splunk connector configured in NCP platform**
- Access to NCP platform with Splunk integration
- Understanding of network operations concepts

### Installation

```bash
# Navigate to the agent directory
cd splunk-connector-agent

# Install dependencies
pip install -r requirements.txt

# Validate the agent
ncp validate .

# Authenticate with NCP platform (if not already done)
ncp authenticate

# Package the agent
ncp package .

# Deploy to NCP platform
ncp deploy splunk-connector-agent.ncp
```

---

## 📁 Project Structure

```
splunk-connector-agent/
├── README.md
├── ncp.toml
├── requirements.txt
├── .gitignore
└── agents/
    ├── __init__.py
    └── main_agent.py
```

**Note**: No `tools/` directory! All tools come from the Splunk connector.

---

## 🔧 Understanding Connectors

### What is a Connector?

A **connector** is a pre-configured MCP server managed by the NCP platform. Instead of configuring MCP servers directly in your agent code, you reference a connector by name, and the platform handles the connection details.

**Traditional MCP Approach (weather-agent):**
```python
from ncp import Agent, MCPConfig

agent = Agent(
    name="weather-agent",
    mcp_servers=[
        MCPConfig(
            command="mcp-server-fetch",
            transport_type="stdio",
            args=[],
            env=None
        )
    ],
    tools=[]
)
```

**Connector Approach (splunk-connector-agent):**
```toml

```python
from ncp import Agent

agent = Agent(
    name="splunk-connector-agent",
    tools=[],
    connectors=["Splunk"]
)
```

### Benefits of Connectors

1. **Centralized Configuration**: Platform admins configure once, all agents use it
2. **Credential Management**: Secrets managed securely by the platform
3. **Version Control**: Update connector without changing agent code
4. **Access Control**: Platform can control which agents access which connectors
5. **Simplified Deployment**: No need to bundle MCP server dependencies

### Connectors vs. MCP Servers

**Without Connectors (Manual MCP):**
- ❌ Each agent configures MCP servers independently
- ❌ Credentials hardcoded or in agent config
- ❌ Updates require changing every agent
- ❌ No centralized access control

**With Connectors (Platform-Managed):**
- ✅ Configure once at platform level
- ✅ Credentials managed securely by platform
- ✅ Update connector, all agents benefit
- ✅ Platform controls access per agent

**The Insight**: Connectors shift operational complexity from agent developers to platform administrators, enabling better security, maintainability, and governance.

---

## 🧠 Key Concepts

### 1. SPL Query Structure

A typical Splunk query follows this pattern:

```
index=<index_name> <search_terms> <field_filters> earliest=<time> | <commands>
```

**Example breakdown:**
```
index=network BGP down host=spine-* earliest=-24h | stats count by host | sort -count
│            │       │    │               │             │                │
│            │       │    │               │             │                └─ Sort by count (descending)
│            │       │    │               │             └─ Aggregate: count events per host
│            │       │    │               └─ Time range: last 24 hours
│            │       │    └─ Field filter: hosts starting with "spine-"
│            │       └─ Search term: "down"
│            └─ Search term: "BGP"
└─ Which index to search
```

### 2. Time Ranges

Always specify time ranges to make searches efficient:

```
earliest=-15m    # Last 15 minutes
earliest=-1h     # Last hour
earliest=-4h     # Last 4 hours
earliest=-24h    # Last 24 hours
earliest=-7d     # Last 7 days
earliest=-30d    # Last 30 days
earliest="2024-01-15:14:00:00" latest="2024-01-15:16:00:00"  # Specific window
```

### 3. Common SPL Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `stats` | Aggregate data | `stats count by host` |
| `timechart` | Time-series data | `timechart span=1h count` |
| `top` | Most common values | `top 10 error_message` |
| `table` | Display specific fields | `table _time, host, message` |
| `sort` | Order results | `sort -count` |
| `head` | Limit results | `head 20` |
| `dedup` | Remove duplicates | `dedup host` |
| `where` | Filter results | `where count > 100` |
| `eval` | Create calculated fields | `eval duration=end-start` |


## 📚 Code Deep Dive

### Agent Structure

```python
from ncp import Agent

agent = Agent(
    name="splunk-connector-agent",
    description="Network operations assistant for Splunk log searching",
    instructions="""
    [Comprehensive SPL instructions...]

    - Search syntax
    - Common commands
    - Network-specific patterns
    - Best practices
    - Response style
    """,
    tools=[]  # Empty! Tools come from connector
    connectors=["Splunk"]  # Use the Splunk connector configured in the platform
)
```

**Key differences from previous examples:**
1. **No custom tools**: The `tools=[]` list is empty
2. **No MCP servers configured**: Connector handles this
3. **Instructions-heavy**: Since no custom tools, instructions guide SPL usage
4. **Platform dependency**: Requires platform-configured connector


## 🚀 Next Steps

### Immediate Next Steps
1. Deploy the agent to your NCP platform
2. Verify Splunk connector access
3. Run example searches to familiarize with SPL
4. Explore your actual network data 
5. Create custom searches for your environment

## 📖 Additional Resources

### Splunk Resources
- [Splunk Search Reference](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/)
- [SPL Quick Reference Guide](https://www.splunk.com/pdfs/solution-guides/splunk-quick-reference-guide.pdf)
- [Splunk Search Tutorial](https://docs.splunk.com/Documentation/Splunk/latest/SearchTutorial/)

### SPL Performance Tips
- Always specify time ranges
- Filter early (use indexed fields)
- Avoid wildcards at start of search terms
- Use `tstats` for metric data
- Limit search scope with indexes
