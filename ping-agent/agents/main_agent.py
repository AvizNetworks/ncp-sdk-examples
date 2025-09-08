"""Main agent for ping-agent."""

from ncp import Agent
from tools.sample_tools import ping_host

# Create your main agent
main_agent = Agent(
    name="PingAgent",
    description="PingAgent is an agent that can ping hosts and process text.",
    instructions="You can use the ping_host tool to ping a host",
    tools=[ping_host],
)
