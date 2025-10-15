"""
Async tools demonstrating concurrent HTTP requests with the NCP SDK.

This module showcases async/await patterns for I/O-bound operations,
specifically concurrent URL fetching using aiohttp and asyncio.gather().
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from ncp import tool


@tool
async def fetch_multiple_urls(urls: List[str]) -> Dict[str, Any]:
    """
    Fetch multiple URLs concurrently using async HTTP requests.

    This tool demonstrates async I/O for network operations. All URLs are fetched
    in parallel, significantly improving performance over sequential requests.

    Args:
        urls: List of URLs to fetch concurrently

    Returns:
        Dictionary containing:
        - results: List of dicts with url, status, content_length, and preview
        - total_urls: Number of URLs requested
        - successful: Number of successful fetches
        - failed: Number of failed fetches
        - total_time_seconds: Time taken for all requests

    Example:
        >>> fetch_multiple_urls([
        ...     "https://api.github.com",
        ...     "https://httpbin.org/json",
        ...     "https://jsonplaceholder.typicode.com/posts/1"
        ... ])
    """
    start_time = time.time()

    async def fetch_one(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Helper to fetch a single URL."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                content = await response.text()
                return {
                    "url": url,
                    "status": response.status,
                    "success": True,
                    "content_length": len(content),
                    "preview": content[:200] + "..." if len(content) > 200 else content,
                    "error": None
                }
        except asyncio.TimeoutError:
            return {
                "url": url,
                "status": None,
                "success": False,
                "content_length": 0,
                "preview": None,
                "error": "Request timed out after 10 seconds"
            }
        except Exception as e:
            return {
                "url": url,
                "status": None,
                "success": False,
                "content_length": 0,
                "preview": None,
                "error": f"{type(e).__name__}: {str(e)}"
            }

    # Create session and fetch all URLs concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    return {
        "results": results,
        "total_urls": len(urls),
        "successful": successful,
        "failed": failed,
        "total_time_seconds": round(total_time, 2)
    }
