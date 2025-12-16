"""Writing tools for the writing specialist agent."""

from ncp import tool


@tool
def format_document(content: str, format_type: str) -> dict:
    """Format content into a specific document structure.

    Args:
        content: The content to format
        format_type: Type of formatting - "email", "report", "list", "summary"

    Returns:
        Formatted document structure
    """
    formats = {
        "email": {
            "structure": ["subject", "greeting", "body", "closing", "signature"],
            "template": f"Subject: [Topic]\n\nDear [Recipient],\n\n{content}\n\nBest regards,\n[Your Name]"
        },
        "report": {
            "structure": ["title", "executive_summary", "findings", "recommendations", "conclusion"],
            "template": f"# Report\n\n## Executive Summary\n{content}\n\n## Findings\n[Details]\n\n## Recommendations\n[Actions]"
        },
        "list": {
            "structure": ["title", "items"],
            "template": f"## List\n\n" + "\n".join(f"- {line.strip()}" for line in content.split(",") if line.strip())
        },
        "summary": {
            "structure": ["overview", "key_points", "conclusion"],
            "template": f"## Summary\n\n**Overview:** {content}\n\n**Key Points:**\n- Point 1\n- Point 2\n\n**Conclusion:** [Wrap up]"
        }
    }

    fmt = formats.get(format_type.lower(), formats["summary"])
    return {
        "format": format_type,
        "structure": fmt["structure"],
        "formatted_content": fmt["template"],
        "original_content": content
    }


@tool
def check_grammar(text: str) -> dict:
    """Check text for grammar and style suggestions.

    Args:
        text: The text to check

    Returns:
        Grammar check results with suggestions
    """
    # Simulated grammar check
    suggestions = []

    # Simple checks for demo
    if "  " in text:
        suggestions.append("Found double spaces - consider removing extra spaces")
    if text and not text[0].isupper():
        suggestions.append("Consider capitalizing the first letter")
    if text and text[-1] not in ".!?":
        suggestions.append("Consider adding punctuation at the end")

    word_count = len(text.split())
    sentence_count = text.count(".") + text.count("!") + text.count("?")

    return {
        "text_length": len(text),
        "word_count": word_count,
        "sentence_count": max(1, sentence_count),
        "avg_words_per_sentence": word_count / max(1, sentence_count),
        "suggestions": suggestions if suggestions else ["No issues found - text looks good!"],
        "status": "clean" if not suggestions else "has_suggestions"
    }


@tool
def generate_outline(topic: str, sections: int = 5) -> dict:
    """Generate an outline for a document.

    Args:
        topic: The main topic for the outline
        sections: Number of main sections (default: 5)

    Returns:
        A structured outline
    """
    # Generate a basic outline structure
    outline = {
        "topic": topic,
        "sections": [
            {"number": 1, "title": "Introduction", "description": f"Introduce {topic} and its importance"},
            {"number": 2, "title": "Background", "description": "Historical context and foundational concepts"},
            {"number": 3, "title": "Main Content", "description": f"Core information about {topic}"},
            {"number": 4, "title": "Analysis", "description": "Critical examination and insights"},
            {"number": 5, "title": "Conclusion", "description": "Summary and future directions"},
        ][:sections]
    }

    return outline
