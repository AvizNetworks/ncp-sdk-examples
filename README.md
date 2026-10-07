# NCP SDK Examples

**Learn by doing: hands-on examples for building AI agents with the NCP SDK**

This repository contains complete, working examples that demonstrate how to build AI agents using the [NCP SDK](https://pypi.org/project/ncp-sdk/0.2.4/). Each example is designed to teach specific concepts while providing production-ready code you can learn from.

---

## 🎯 Getting Started

### Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **pip** package manager
- **ncp-sdk** installed (`pip install ncp-sdk`)

### Quick Setup

```bash
# Clone this repository
git clone <repository-url>
cd ncp-sdk-examples

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install NCP SDK
pip install ncp-sdk

# Verify installation
ncp --help
```

## 📖 How to Use These Examples

### Learning Path

We recommend following this sequence:

1. **Start with hello-agent** - Learn the basics
2. **Pick examples by interest** - Choose what's relevant to you
3. **Modify and experiment** - Best way to learn!
4. **Build your own** - Apply what you've learned

### Each Example Includes

- ✅ **Comprehensive README**: Step-by-step tutorial
- ✅ **Complete Code**: Production-ready, commented
- ✅ **Project Structure**: Standard NCP SDK layout
- ✅ **Example Interactions**: See what it does
- ✅ **Key Takeaways**: What you learned
- ✅ **Next Steps**: How to extend it

### Running an Example

```bash
# Navigate to the example
cd <example-name>

# Install dependencies
pip install -r requirements.txt

# Validate the project
ncp validate .

# Deploy to platform
ncp authenticate
ncp package .
ncp deploy <example-name>.ncp
```

---

## 🛠️ Development Workflow

### Common Commands

```bash
# Validate your agent
ncp validate .

# Package for deployment
ncp package .

# Authenticate with platform
ncp authenticate

# Deploy to platform
ncp deploy <agent>.ncp

# Test interactively
ncp playground --agent <agent-name>

# Remove agent
ncp remove --agent <agent-name>
```

### Offline Packages (Air-Gapped Servers)

If the NCP server has no internet access, it cannot download the packages
listed in `requirements.txt` and `apt-requirements.txt`. Build an offline
package instead. It bundles every apt package and Python wheel the agent
needs, so the server installs from the package alone (ncp-sdk 1.5.0 or later,
and Docker on the build machine):

```bash
cd file-agent
ncp package . --offline                          # amd64 NCP server (default)
ncp package . --offline --platform linux/arm64   # arm64 NCP server
ncp deploy file-agent.ncp                        # or: ncp onboard file-agent.ncp
```

This works the same from macOS (Intel or Apple Silicon) and Linux. Before the
package is written, the bundle is test-installed in a container with no
network. See [Offline Packages](https://github.com/AvizNetworks/ncp-sdk#offline-packages-air-gapped-servers)
in the SDK guide for how it works and its limitations.
