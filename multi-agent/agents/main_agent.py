"""Multi-Agent Example - Orchestrator with specialized child agents.

This example demonstrates how to build a multi-agent system using AgentTool.
An orchestrator agent delegates tasks to specialized child agents:
- Math Agent: Handles calculations and unit conversions
- Research Agent: Searches knowledge and provides summaries
- Writing Agent: Formats documents and checks grammar

The orchestrator decides which specialist to delegate to based on the user's request.
"""

from ncp import Agent, AgentTool
from tools.math_tools import calculate, convert_units
from tools.research_tools import search_knowledge, summarize_topic
from tools.writing_tools import format_document, check_grammar, generate_outline


# =============================================================================
# Step 1: Define Specialized Child Agents
# =============================================================================

# Math Specialist Agent
math_agent = Agent(
    name="math_specialist",
    description="Expert at mathematical calculations, unit conversions, and numeric analysis",
    instructions="""You are a math specialist. Your expertise includes:
- Arithmetic calculations (addition, subtraction, multiplication, division)
- Unit conversions (length, weight, temperature)
- Breaking down complex math problems into steps

When solving problems:
1. Identify what needs to be calculated
2. Use the appropriate tool for each step
3. Show your work clearly
4. Verify your answer makes sense

Be precise with numbers and explain your reasoning.""",
    tools=[calculate, convert_units],
)

# Research Specialist Agent
research_agent = Agent(
    name="research_specialist",
    description="Expert at finding information, researching topics, and providing summaries",
    instructions="""You are a research specialist. Your expertise includes:
- Searching for information on various topics
- Summarizing complex subjects
- Providing clear, factual explanations

When researching:
1. Search for relevant information
2. Organize findings logically
3. Provide clear summaries
4. Cite your sources when available

Be thorough and accurate in your research.""",
    tools=[search_knowledge, summarize_topic],
)

# Writing Specialist Agent
writing_agent = Agent(
    name="writing_specialist",
    description="Expert at writing, formatting documents, and improving text quality",
    instructions="""You are a writing specialist. Your expertise includes:
- Formatting content into various document types
- Checking grammar and style
- Creating document outlines
- Improving text clarity

When helping with writing:
1. Understand the desired format and audience
2. Use appropriate tools to format or check content
3. Provide constructive suggestions
4. Maintain the author's voice while improving quality

Be helpful and constructive with feedback.""",
    tools=[format_document, check_grammar, generate_outline],
)


# =============================================================================
# Step 2: Wrap Agents as Tools using AgentTool
# =============================================================================

# Create AgentTools from the specialized agents
math_tool = AgentTool(
    math_agent,
    name="math_expert",
    description="Delegate math problems, calculations, and unit conversions to the math specialist"
)

research_tool = AgentTool(
    research_agent,
    name="research_expert",
    description="Delegate research questions, topic exploration, and information lookup to the research specialist"
)

writing_tool = AgentTool(
    writing_agent,
    name="writing_expert",
    description="Delegate writing tasks, document formatting, and grammar checking to the writing specialist"
)


# =============================================================================
# Step 3: Create the Orchestrator Agent
# =============================================================================

agent = Agent(
    name="MultiAgentOrchestrator",
    description="An intelligent assistant that coordinates specialized agents to handle diverse tasks",
    instructions="""You are an orchestrator that coordinates a team of specialist agents.

Your team includes:
1. **Math Expert** - For calculations, unit conversions, and numeric problems
2. **Research Expert** - For finding information, researching topics, and summaries
3. **Writing Expert** - For document formatting, grammar checking, and outlines

How to work:
1. Analyze the user's request to understand what they need
2. Determine which specialist(s) can best help
3. Delegate to the appropriate expert(s) using the tools
4. Synthesize the results into a helpful response

Delegation guidelines:
- Math questions → math_expert
- "What is...", "Tell me about...", "Research..." → research_expert
- "Write...", "Format...", "Check my grammar..." → writing_expert
- Complex requests may need multiple experts

You can delegate to multiple experts if needed. For example:
- "Research AI and write a summary" → research_expert then writing_expert
- "Calculate 15% of $200 and explain the math" → math_expert

Be helpful, coordinate effectively, and provide complete answers.""",
    tools=[math_tool, research_tool, writing_tool],
)
