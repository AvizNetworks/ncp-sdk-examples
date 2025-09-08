# ping-agent

A custom NCP agent project.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your agent in `agents/main_agent.py`

3. Add custom tools in the `tools/` directory

4. Add system dependencies in `apt-requirements.txt` if needed

## Dependencies

- **requirements.txt**: Python packages (pandas, numpy, requests, etc.)
- **apt-requirements.txt**: System packages (curl, git, ffmpeg, etc.)

## Development

```bash
# Validate your project
ncp validate .

# Package for deployment  
ncp package . --output ping-agent.ncp

# Deploy to NCP platform
ncp deploy ping-agent.ncp --platform https://your-ncp-instance.com
```

## Project Structure

- `agents/` - Agent definitions
- `tools/` - Custom tool implementations
- `requirements.txt` - Python dependencies
- `ncp.toml` - Project configuration
