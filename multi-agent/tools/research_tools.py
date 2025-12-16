"""Research tools for the research specialist agent."""

from ncp import tool


@tool
def search_knowledge(query: str) -> dict:
    """Search for information on a topic.

    Simulates searching a knowledge base for relevant information.

    Args:
        query: The search query

    Returns:
        Search results with relevant information
    """
    # Simulated knowledge base for demo purposes
    knowledge = {
        "python": {
            "topic": "Python Programming",
            "summary": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
            "key_facts": [
                "Created by Guido van Rossum in 1991",
                "Used for web development, data science, AI, and automation",
                "Known for its clean syntax and extensive standard library"
            ]
        },
        "machine learning": {
            "topic": "Machine Learning",
            "summary": "Machine learning is a subset of AI that enables systems to learn from data.",
            "key_facts": [
                "Types: supervised, unsupervised, reinforcement learning",
                "Common algorithms: neural networks, decision trees, SVM",
                "Applications: image recognition, NLP, recommendation systems"
            ]
        },
        "networking": {
            "topic": "Computer Networking",
            "summary": "Networking involves connecting computers to share resources and communicate.",
            "key_facts": [
                "OSI model has 7 layers",
                "TCP/IP is the foundation of the internet",
                "Common protocols: HTTP, DNS, DHCP, SSH"
            ]
        }
    }

    # Search for matching topics
    query_lower = query.lower()
    for key, info in knowledge.items():
        if key in query_lower or query_lower in key:
            return {"found": True, **info}

    return {
        "found": False,
        "message": f"No specific information found for '{query}'. Try: python, machine learning, or networking."
    }


@tool
def summarize_topic(topic: str, length: str = "medium") -> dict:
    """Generate a summary about a topic.

    Args:
        topic: The topic to summarize
        length: Summary length - "short", "medium", or "long"

    Returns:
        A structured summary of the topic
    """
    summaries = {
        "ai": {
            "short": "AI enables machines to simulate human intelligence.",
            "medium": "Artificial Intelligence (AI) is the simulation of human intelligence by machines. It includes learning, reasoning, and self-correction capabilities.",
            "long": "Artificial Intelligence (AI) is a broad field of computer science focused on building smart machines capable of performing tasks that typically require human intelligence. This includes machine learning, natural language processing, computer vision, and robotics. AI systems can analyze large amounts of data, recognize patterns, and make decisions with minimal human intervention."
        },
        "cloud": {
            "short": "Cloud computing delivers computing services over the internet.",
            "medium": "Cloud computing provides on-demand access to computing resources like servers, storage, and applications over the internet, enabling scalability and cost efficiency.",
            "long": "Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the internet. It offers faster innovation, flexible resources, and economies of scale. Major providers include AWS, Azure, and Google Cloud Platform."
        }
    }

    topic_lower = topic.lower()
    for key, lengths in summaries.items():
        if key in topic_lower:
            return {
                "topic": topic,
                "length": length,
                "summary": lengths.get(length, lengths["medium"])
            }

    return {
        "topic": topic,
        "length": length,
        "summary": f"[Demo] A {length} summary about {topic} would go here."
    }
