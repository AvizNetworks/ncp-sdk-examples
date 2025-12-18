"""Main agent definition for Weather Agent.

This agent demonstrates MCP (Model Context Protocol) integration by using
an external MCP server to fetch weather data without writing custom Python tools.
"""

from ncp import Agent, tool

@tool
def get_weather(name: str):
    return {"name": name, "weather": "23 C, sunny"}


# Define the weather agent with MCP server configuration
agent = Agent(
    name="WeatherAgent",
    description="A weather assistant that fetches real-time weather information using MCP",
    instructions="""You are a helpful weather assistant""",
    tools=[get_weather],
)
