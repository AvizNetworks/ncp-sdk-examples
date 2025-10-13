"""Greeting tools for the hello-agent."""

from ncp import tool


@tool
def say_hello(name: str) -> str:
    """Say hello to someone by name.

    This tool generates a personalized greeting for any person.
    Use this tool after identifying who needs to be greeted.

    Args:
        name: The full name of the person to greet (e.g., "John Doe", "Jane Smith")

    Returns:
        A friendly greeting message for the specified person

    Examples:
        >>> say_hello("Alice")
        "Hello, Alice! Nice to meet you!"

        >>> say_hello("Bob Smith")
        "Hello, Bob Smith! Nice to meet you!"
    """
    return f"Hello, {name}! Nice to meet you!"
