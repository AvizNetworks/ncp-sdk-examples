"""Main agent definition for Weather Agent.

This agent demonstrates MCP (Model Context Protocol) integration by using
an external MCP server to fetch weather data without writing custom Python tools.
"""

from ncp import Agent, MCPConfig


# Define the weather agent with MCP server configuration
agent = Agent(
    name="WeatherAgent",
    description="A weather assistant that fetches real-time weather information using MCP",
    instructions="""You are a helpful weather assistant that provides current weather information for any city.

You have access to the 'fetch' tool from the MCP server which allows you to make HTTP requests.

To get weather information:
1. Use the fetch tool to call: https://wttr.in/{city}?format=j1
   - Replace {city} with the city name (e.g., "London", "New York", "Tokyo")
   - This returns detailed weather data in JSON format

2. Parse the JSON response to extract:
   - Current temperature (temp_C or temp_F)
   - Weather description (weatherDesc)
   - Feels like temperature (FeelsLikeC or FeelsLikeF)
   - Humidity
   - Wind speed and direction
   - Visibility

3. Present the weather information in a friendly, conversational way

Examples of how to use the fetch tool:
- For London: fetch(url="https://wttr.in/London?format=j1")
- For New York: fetch(url="https://wttr.in/New York?format=j1")
- For Tokyo: fetch(url="https://wttr.in/Tokyo?format=j1")

Always be helpful and explain the weather conditions clearly. If the fetch fails or the city is not found, explain this to the user politely.""",
    tools=[],  # No custom Python tools - using MCP tools only
    mcp_servers=[
        MCPConfig(
            command="mcp-server-fetch",
            transport_type="stdio",
            args=[],
            env=None,
        )
    ],
)
