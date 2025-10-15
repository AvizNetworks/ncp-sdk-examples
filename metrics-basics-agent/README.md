# Metrics Basics Agent


## 🎯 What You'll Learn

- **Metrics API Fundamentals**: Query network device inventory and operational data
- **Device Discovery**: Find devices by layer, region, or other criteria
- **Interface Queries**: List and analyze network interfaces
- **Structured Data Handling**: Work with comprehensive device information
- **API Patterns**: Initialize clients, query data, interpret results

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- NCP SDK installed (`pip install ncp-sdk`)
- Access to NCP platform with Metrics API
- Understanding of network device concepts (spine/leaf, interfaces)

### Installation

```bash
# Navigate to the agent directory
cd metrics-basics-agent

# Install dependencies
pip install -r requirements.txt

# Validate the agent
ncp validate .

# Authenticate with NCP platform (if not already done)
ncp authenticate

# Package the agent
ncp package .

# Deploy to NCP platform
ncp deploy metrics-basics-agent.ncp
```

---

## 📁 Project Structure

```
metrics-basics-agent/
├── README.md              # This file
├── ncp.toml              # Project configuration
├── requirements.txt       # Python dependencies (ncp-sdk)
├── .gitignore            # Protect credentials
├── agents/
│   ├── __init__.py
│   └── main_agent.py     # Agent definition with Metrics instructions
└── tools/
    ├── __init__.py
    └── metrics_tools.py  # 4 custom tools using Metrics API
```

---

## 🔧 The Tools

### 1. `get_device_inventory(layer, region)`

Query all devices in the network inventory with optional filtering.

**Parameters:**
- `layer` (optional): Filter by device layer ("spine", "leaf", "border")
- `region` (optional): Filter by region/datacenter

**Returns:**
- `devices`: List of device objects with details
- `total_count`: Number of devices found
- `filters_applied`: Which filters were used

**Use Cases:**
- "Show me all devices"
- "List all spine switches"
- "What devices are in datacenter-1?"

---

### 2. `check_device_status(hostname)`

Check the operational status of a specific network device.

**Parameters:**
- `hostname` (required): Device hostname to check

**Returns:**
- Reachability status
- Uptime information
- Basic health metrics (CPU, memory, temperature)
- Management IP and device info

**Use Cases:**
- "Is spine-01 reachable?"
- "Check if leaf-03 is up"
- "What's the uptime of border-01?"

---

### 3. `list_interfaces(hostname, status)`

List all network interfaces on a device with optional status filtering.

**Parameters:**
- `hostname` (required): Device hostname
- `status` (optional): Filter by interface status ("up", "down")

**Returns:**
- Interface list with names, status, speed, description
- Traffic statistics (input/output rates)
- Error counters
- Summary of up/down interfaces

**Use Cases:**
- "List all interfaces on spine-01"
- "Show me down interfaces on leaf-03"
- "What interfaces have errors?"

---

### 4. `get_device_details(hostname)`

Get comprehensive information about a network device.

**Parameters:**
- `hostname` (required): Device hostname

**Returns:**
- Basic info (hostname, model, layer, region)
- Hardware specs (model, ports, serial number)
- Software versions (OS, config version)
- Performance metrics (CPU, memory, temperature)
- Interfaces summary
- Connectivity info (BGP peers, LLDP neighbors)

**Use Cases:**
- "Tell me everything about spine-01"
- "What model is leaf-03?"
- "Show full details for border-01"

---

## 📚 Code Deep Dive

### Metrics API Pattern

The Metrics API implementation uses proper resource management:

```python
from ncp.metrics import Metrics

@tool
def get_device_inventory(layer: Optional[str] = None):
    # Initialize client
    metrics = Metrics()

    try:
        # Build query parameters
        kwargs = {}
        if layer:
            kwargs["layer"] = layer

        # Execute query - filters are passed as keyword arguments
        devices = metrics.get_devices(**kwargs)

        return {
            "devices": devices,
            "total_count": len(devices)
        }
    finally:
        # Always close client to free resources
        metrics.close()
```

**Key Pattern**: Filter parameters are passed as keyword arguments (`**kwargs`), not as a `filters` dictionary. Always use `try/finally` to ensure proper resource cleanup.

### Agent Instructions Structure

The agent instructions are organized in sections:

1. **Tool Descriptions**: What each tool does
2. **Usage Patterns**: When to use which tool
3. **Workflows**: Step-by-step guidance
4. **Response Style**: How to format answers
5. **Examples**: Concrete interaction patterns

This comprehensive guidance helps the LLM use tools effectively.

---

## 🔬 Try It Yourself

### Exercise 1: Basic Inventory
Deploy the agent and ask:
```
Show me all devices
```

**Learning Goal**: See how the agent structures inventory data.

---

### Exercise 2: Status Checking
Try:
```
Is spine-01 working?
Check the status of leaf-07
```

**Learning Goal**: Observe status interpretation and health metrics.

---

### Exercise 3: Interface Investigation
Ask:
```
List all interfaces on spine-01
Show me down interfaces on spine-01
```

**Learning Goal**: Understand interface data and error analysis.

---

### Exercise 4: Layer Filtering
Try:
```
Show me all spine switches
List all leaf switches
```

**Learning Goal**: See how layer filtering works.

---

### Exercise 5: Comprehensive Analysis
Ask:
```
Tell me everything about leaf-03
```

**Learning Goal**: See how the agent combines multiple data points into a coherent summary.

---

### Exercise 6: Troubleshooting Workflow
Multi-step investigation:
```
1. "Show me all devices"
2. Notice leaf-07 is down
3. "Check the status of leaf-07"
4. "List interfaces on leaf-07"
5. "Get full details for leaf-07"
```

**Learning Goal**: Practice systematic troubleshooting workflow.

---

## 🚀 Next Steps

### Immediate Next Steps
1. Deploy and test the agent
2. Explore device inventory in your environment
3. Practice filtering by layer and region
4. Investigate device status and interfaces
5. Build troubleshooting workflows

### Extend This Example

**Idea 1: Add Alerting Logic**
Extend tools to identify issues:
```python
@tool
def find_unhealthy_devices():
    """Find devices with issues."""
    inventory = get_device_inventory()
    issues = []
    for device in inventory["devices"]:
        if not device["reachable"]:
            issues.append({"device": device, "issue": "unreachable"})
    return issues
```

**Idea 2: Add Capacity Analysis**
```python
@tool
def analyze_capacity():
    """Check device resource utilization."""
    # Query all devices
    # Check CPU/memory thresholds
    # Return devices near capacity
```

**Idea 3: Combine with Splunk**
Create a troubleshooting agent that uses both:
1. Metrics API to check current state
2. Splunk to find historical errors
3. Correlate state changes with log events

**Idea 4: Add Time-Series Queries**
Extend to query historical metrics:
```python
@tool
def get_cpu_history(hostname: str, hours: int = 24):
    """Get CPU utilization trend."""
    # Query time-series data
    # Return DataFrame or time-series points
```
