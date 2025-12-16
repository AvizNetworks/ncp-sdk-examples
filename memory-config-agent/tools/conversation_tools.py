"""Conversation tools for demonstrating memory configuration.

These tools help track conversation context to show how memory
strategies affect what the agent remembers across turns.
"""

from ncp import tool


@tool
def remember_fact(key: str, value: str) -> dict:
    """Store a fact that the user wants to remember.

    Use this to help the user save important information during the conversation.
    The agent should recall these facts when relevant.

    Args:
        key: A short label for the fact (e.g., "favorite_color", "pet_name")
        value: The actual information to remember

    Returns:
        Confirmation that the fact was noted
    """
    return {
        "status": "noted",
        "key": key,
        "value": value,
        "message": f"I've noted that {key} is '{value}'. I'll remember this."
    }


@tool
def get_current_context(topic: str) -> dict:
    """Summarize the current conversation context about a topic.

    Use this to check what has been discussed about a specific topic
    in the current conversation.

    Args:
        topic: The topic to summarize context for

    Returns:
        A prompt for the agent to recall relevant context
    """
    return {
        "action": "recall_context",
        "topic": topic,
        "instruction": f"Based on our conversation, summarize what we've discussed about '{topic}'."
    }


@tool
def lookup_info(query: str) -> dict:
    """Look up information (simulated).

    This simulates an external lookup. In a real agent, this might
    call an API or database.

    Args:
        query: What to look up

    Returns:
        Simulated lookup result
    """
    # Simulated responses for demo purposes
    responses = {
        "weather": "Current weather: 72F, sunny with light clouds.",
        "time": "Current time: 2:30 PM PST",
        "news": "Top story: Technology advances continue to reshape industries.",
    }

    for key, response in responses.items():
        if key in query.lower():
            return {"found": True, "result": response}

    return {
        "found": False,
        "result": f"No specific data found for '{query}'. This is a demo tool."
    }
