"""Sample tools for NCP agents."""

from ncp import tool
import subprocess

@tool
def ping_host(host: str) -> str:
    """Ping a host and return the result."""
    try:
        result = subprocess.run(['ping', '-c', '4', host], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error pinging {host}: {e.stderr}"