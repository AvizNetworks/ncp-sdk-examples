"""Main agent definition demonstrating memory configuration.

This example shows how to configure different memory strategies:
- TOKEN_WINDOW: Token-budget based context management (default)
- LAST_N_MESSAGES: Fixed message count based context

Memory strategies control how much conversation history the agent
retains in its context window.
"""

from ncp import Agent, MemoryConfig, STMStrategy
from tools.conversation_tools import remember_fact, get_current_context, lookup_info


# =============================================================================
# Option 1: TOKEN_WINDOW Strategy (Default)
# =============================================================================
# Best for: Long conversations where you want to maximize context usage
# How it works: Keeps as many messages as fit within the token budget
#
# Configuration:
#   - max_context_tokens: Model's context window size (default: 131072)
#   - generation_buffer: Fraction reserved for model output (default: 0.25)
#   - tool_tokens: Reserved for tool schemas (managed automatically)

token_window_config = MemoryConfig(
    stm_enabled=True,
    stm_strategy=STMStrategy.TOKEN_WINDOW,
    stm_config={
        "max_context_tokens": 131072,  # 128K context window
        "generation_buffer": 0.25,      # Reserve 25% for generation
        "tool_tokens": 0,               # Updated dynamically by platform
    }
)


# =============================================================================
# Option 2: LAST_N_MESSAGES Strategy
# =============================================================================
# Best for: Predictable context size, simpler memory management
# How it works: Keeps the last N conversation "turns"
#
# A "turn" includes:
#   - User message
#   - Tool calls (if any)
#   - Tool results (if any)
#   - Assistant response
#
# Configuration:
#   - max_messages: Number of turns to keep (default: 20)
#   - include_tools: Whether to include tool calls in context (default: True)

last_n_messages_config = MemoryConfig(
    stm_enabled=True,
    stm_strategy=STMStrategy.LAST_N_MESSAGES,
    stm_config={
        "max_messages": 20,      # Keep last 20 conversation turns
        "include_tools": True,   # Include tool calls and results
    }
)


# =============================================================================
# Option 3: Smaller Context (for shorter conversations)
# =============================================================================
# Use a smaller token budget for cost-effective short conversations

small_context_config = MemoryConfig(
    stm_enabled=True,
    stm_strategy=STMStrategy.TOKEN_WINDOW,
    stm_config={
        "max_context_tokens": 32768,  # 32K context window
        "generation_buffer": 0.30,     # Reserve 30% for generation
        "tool_tokens": 0,
    }
)


# =============================================================================
# Option 4: Stateless Mode (no memory)
# =============================================================================
# Each request is independent - no conversation history retained
# Best for: Single-turn interactions, stateless APIs

stateless_config = MemoryConfig(stm_enabled=False)


# =============================================================================
# The Agent Definition
# =============================================================================
# Change memory_config to experiment with different strategies

agent = Agent(
    name="MemoryConfigAgent",
    description="A conversational assistant that demonstrates memory configuration strategies",
    instructions="""You are a helpful assistant that demonstrates how memory works in AI agents.

Your role:
1. Have natural conversations with users
2. Remember facts they share using the remember_fact tool
3. Help them understand how conversation context is managed
4. Look up information when asked

Memory behavior:
- Your memory configuration determines how much conversation history you retain
- The system message (these instructions) is always preserved
- Recent messages take priority over older ones
- Tool calls and results are part of the context

When users ask about memory:
- Explain that you use short-term memory (STM) to track conversations
- Your memory strategy determines how context is managed
- You don't have persistent long-term memory between sessions

Be conversational and helpful. When demonstrating memory, reference earlier
parts of the conversation to show what you remember.""",
    tools=[remember_fact, get_current_context, lookup_info],
    # Change this to experiment with different memory strategies:
    memory_config=token_window_config,
)
