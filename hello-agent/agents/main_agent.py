"""Main agent definition for Hello Agent.

This agent demonstrates how AI agents combine their built-in knowledge
with custom tools to accomplish tasks.
"""

from ncp import Agent, LLMConfig
from tools.greeting_tools import say_hello


# Define your agent
agent = Agent(
    name="HelloAgent",
    description="A friendly greeting assistant that uses AI knowledge and tools",
    instructions="You are a friendly greeting assistant. Your goal is to greet people by name.",
    tools=[say_hello],
)
