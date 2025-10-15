# Async Tools Agent

> **Tier 2: Core Patterns** - Learn async tool development for concurrent I/O operations

## 🎯 What You'll Learn

- **Async/Await Syntax**: How to write async tools using `async def` and `await`
- **Concurrent Execution**: Using `asyncio.gather()` to run operations in parallel
- **Performance Benefits**: Why async matters for I/O-bound operations
- **Error Handling**: Managing failures in concurrent operations
- **When to Use Async**: Identifying scenarios where async provides value

**Complexity**: ⭐⭐ Intermediate

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- NCP SDK installed (`pip install ncp-sdk`)
- Basic understanding of async/await (we'll explain as we go!)

### Installation

```bash
# Navigate to the agent directory
cd async-tools-agent

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Validate the agent
ncp validate .
```

---

## 📁 Project Structure

```
async-tools-agent/
├── README.md              # This file
├── ncp.toml              # Project configuration
├── requirements.txt       # Python dependencies
├── agents/
│   ├── __init__.py
│   └── main_agent.py     # Agent definition with instructions
└── tools/
    ├── __init__.py
    └── async_tools.py    # Async URL fetching tool
```

---

## 🔧 The Tool

### `fetch_multiple_urls(urls: List[str])`

Fetches multiple URLs concurrently using async HTTP requests.

**Why it's async**: Network I/O is inherently waiting-based. While waiting for one URL to respond, we can make requests to other URLs simultaneously.

**Parameters**:
- `urls`: List of URLs to fetch in parallel

**Returns**: Dictionary with:
- `results`: List of results for each URL (status, content preview, errors)
- `total_urls`: Number of URLs requested
- `successful`: Count of successful fetches
- `failed`: Count of failed fetches
- `total_time_seconds`: Total time for all concurrent requests

**Key Implementation Details**:
```python
@tool
async def fetch_multiple_urls(urls: List[str]) -> Dict[str, Any]:
    # Note the 'async def' - this makes it an async tool

    async with aiohttp.ClientSession() as session:
        # Create tasks for all URLs
        tasks = [fetch_one(session, url) for url in urls]

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)

    return results
```

The magic is in `asyncio.gather(*tasks)` - this runs all URL fetches simultaneously!

---

## 🎬 Example Interactions

### Example 1: Simple Batch Check

**User**: Check if these sites are up: https://api.github.com, https://httpbin.org/status/200, https://jsonplaceholder.typicode.com/todos/1

**Agent Response**:
```
I'll fetch all three URLs concurrently to check their status.

[Calls fetch_multiple_urls with all 3 URLs]

Results:
✅ https://api.github.com - Status 200 (Success)
✅ https://httpbin.org/status/200 - Status 200 (Success)
✅ https://jsonplaceholder.typicode.com/todos/1 - Status 200 (Success)

All 3 sites are up and responding! The concurrent fetch completed in 0.87 seconds.
If we had fetched these sequentially, it would have taken approximately 2-3 seconds.
```

---

### Example 2: Handling Failures Gracefully

**User**: Fetch these URLs: https://google.com, https://thiswebsitedoesnotexist12345.com, https://github.com

**Agent Response**:
```
I'll fetch all three URLs concurrently.

[Calls fetch_multiple_urls]

Results:
✅ https://google.com - Status 200 (Content length: 15234 bytes)
❌ https://thiswebsitedoesnotexist12345.com - Failed (Cannot connect to host)
✅ https://github.com - Status 200 (Content length: 245891 bytes)

Summary: 2 successful, 1 failed
Total time: 1.2 seconds

The non-existent domain failed as expected, but the other two sites loaded successfully.
```

---

### Example 3: API Data Gathering

**User**: Get data from these API endpoints:
- https://api.github.com/users/octocat
- https://jsonplaceholder.typicode.com/users/1
- https://httpbin.org/json

**Agent Response**:
```
I'll fetch all three API endpoints in parallel.

[Calls fetch_multiple_urls]

All three APIs responded successfully in 1.1 seconds:

1. GitHub API (api.github.com):
   - Status: 200
   - Response preview: {"login":"octocat","id":583231,"node_id":"MDQ6VXNlcjU4MzIzMQ=="...

2. JSONPlaceholder API (jsonplaceholder.typicode.com):
   - Status: 200
   - Response preview: {"id":1,"name":"Leanne Graham","username":"Bret"...

3. HTTPBin JSON (httpbin.org):
   - Status: 200
   - Response preview: {"slideshow":{"author":"Yours Truly","date":"date of publication"...

The concurrent approach saved significant time compared to fetching sequentially!
```

---

### Example 4: Performance Comparison

**User**: Fetch 5 different URLs and tell me how long it takes

**Agent Response**:
```
I'll fetch all 5 URLs concurrently and measure the performance.

[Calls fetch_multiple_urls with 5 URLs]

Performance Results:
- Total URLs: 5
- Successful: 5
- Failed: 0
- Total time: 1.34 seconds

Here's why async is powerful: If we had fetched these sequentially (one after another),
and each request took approximately 0.8-1.2 seconds, the total time would have been
4-6 seconds.

By using async tools, we fetched all 5 URLs in parallel, reducing the time to just
1.34 seconds - that's 3-4x faster! This is the power of concurrent I/O operations.
```

---

### Example 5: Error Scenarios

**User**: What happens if some URLs timeout?

**Agent Response**:
```
Let me demonstrate by including some URLs that might timeout:

[Calls fetch_multiple_urls with mix of good and problematic URLs]

Results:
✅ https://api.github.com - Status 200 (847ms)
❌ https://10.255.255.1 - Failed (Request timed out after 10 seconds)
✅ https://httpbin.org/delay/2 - Status 200 (2103ms)
❌ https://httpbin.org/delay/15 - Failed (Request timed out after 10 seconds)

Summary: 2 successful, 2 failed
Total time: 10.2 seconds

The tool handles timeouts gracefully:
- Each URL has a 10-second timeout
- Failed requests don't block successful ones
- You get detailed error messages for failures
- The agent continues with partial results

Even with failures, the async approach ensures that successful requests complete
as quickly as possible without waiting for timeouts to complete sequentially.
```

---

## 💡 The "Aha!" Moment

### Sequential vs. Concurrent: A Visual

**Sequential (Traditional):**
```
Request 1: ████████ (1.2s)
                      Request 2: ████████ (0.9s)
                                          Request 3: ████████ (1.1s)
Total: 3.2 seconds
```

**Concurrent (Async):**
```
Request 1: ████████ (1.2s)
Request 2: ████████ (0.9s)
Request 3: ████████ (1.1s)
Total: 1.2 seconds (longest request)
```

**The Insight**: With async tools, you wait for the *slowest* operation, not the *sum* of all operations!

---

## 🧠 Key Concepts

### 1. What Makes a Tool "Async"?

**Regular Tool:**
```python
@tool
def fetch_url(url: str) -> dict:  # Regular function
    response = requests.get(url)   # Blocks until complete
    return response.json()
```

**Async Tool:**
```python
@tool
async def fetch_url(url: str) -> dict:  # Note 'async def'
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)  # Note 'await'
        return await response.json()
```

The `async def` and `await` keywords enable concurrent execution.

### 2. When to Use Async Tools

**✅ USE ASYNC FOR:**
- Network requests (APIs, web scraping)
- File I/O (reading/writing many files)
- Database queries (multiple queries)
- Any I/O-bound operation where you're waiting for external resources

**❌ DON'T USE ASYNC FOR:**
- CPU-intensive calculations (mathematical computations)
- Local data processing (sorting, filtering in-memory data)
- Operations that don't involve waiting

**Rule of Thumb**: If your tool spends most of its time *waiting* for something external, make it async.

### 3. The `asyncio.gather()` Pattern

This is the core pattern for concurrent execution:

```python
# Create a list of tasks (coroutines)
tasks = [fetch_one(session, url) for url in urls]

# Execute all tasks concurrently and wait for all to complete
results = await asyncio.gather(*tasks)
```

`asyncio.gather()` returns results in the same order as the input tasks, making it easy to match results with inputs.

### 4. Error Handling in Async Tools

Each async operation can fail independently:

```python
async def fetch_one(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            return {"success": True, "data": await response.text()}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

This ensures one failed request doesn't crash the entire batch.

### 5. The NCP SDK Handles Async Automatically

When you decorate a function with `@tool`, the NCP SDK:
- Recognizes `async def` functions
- Creates the proper async event loop
- Handles concurrent execution
- Returns results to the LLM

You just write the async code - the SDK handles the infrastructure!

---

## 📚 Code Deep Dive

### Complete Tool Implementation Walkthrough

```python
@tool
async def fetch_multiple_urls(urls: List[str]) -> Dict[str, Any]:
    start_time = time.time()

    # Helper function to fetch a single URL
    async def fetch_one(session: aiohttp.ClientSession, url: str):
        try:
            # The 'async with' ensures proper cleanup
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
            # Timeout is handled separately for clarity
            return {"url": url, "success": False, "error": "Request timed out"}
        except Exception as e:
            # Catch all other errors
            return {"url": url, "success": False, "error": str(e)}

    # Create a client session (connection pooling, keep-alive)
    async with aiohttp.ClientSession() as session:
        # Create all tasks
        tasks = [fetch_one(session, url) for url in urls]
        # Execute concurrently
        results = await asyncio.gather(*tasks)

    # Calculate metrics
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r["success"])

    return {
        "results": results,
        "total_urls": len(urls),
        "successful": successful,
        "failed": len(results) - successful,
        "total_time_seconds": round(total_time, 2)
    }
```

### Agent Instructions Breakdown

The agent instructions guide the LLM on:

1. **Tool Capabilities**: What the tool does and why it's async
2. **Usage Patterns**: How to call the tool effectively (batch all URLs in one call)
3. **Error Handling**: What to do when some requests fail
4. **Performance Context**: Explaining timing benefits to users
5. **Best Practices**: When to use async vs. sequential

---

## 🔬 Try It Yourself

### Exercise 1: Basic Usage
Deploy the agent and try:
```
Fetch these URLs:
- https://api.github.com
- https://httpbin.org/json
- https://jsonplaceholder.typicode.com/posts/1
```

**Learning Goal**: See how the agent batches requests and reports timing.

---

### Exercise 2: Error Handling
Try:
```
Check if these URLs are accessible:
- https://google.com (valid)
- https://invalid-url-xyz-12345.com (invalid)
- https://github.com (valid)
```

**Learning Goal**: Observe how the agent handles partial failures gracefully.

---

### Exercise 3: Performance Comparison
Ask:
```
Fetch 10 different URLs and show me how long it takes
```

Then ask:
```
How much faster is this compared to fetching them one by one?
```

**Learning Goal**: Understand the performance benefits of async operations.

---

### Exercise 4: Extend the Tool

**Challenge**: Add a new async tool called `check_website_status()` that:
- Takes a list of URLs
- Only checks if they return 200 (doesn't download content)
- Uses HEAD requests instead of GET (faster)
- Returns a simple up/down report

**Implementation Hints**:
```python
@tool
async def check_website_status(urls: List[str]) -> Dict[str, Any]:
    async def check_one(session, url):
        try:
            async with session.head(url, timeout=5) as response:
                return {"url": url, "status": "up" if response.status == 200 else "down"}
        except:
            return {"url": url, "status": "down"}

    # Implement the rest...
```

---

### Exercise 5: Real-World Scenario

**Scenario**: You're building a monitoring dashboard that needs to check 20 microservice health endpoints every minute.

**Tasks**:
1. Use the agent to fetch 20 URLs (you can use httpbin.org/delay/X with different delays)
2. Calculate how long it takes
3. Estimate: Could you check all 20 services within a 60-second window?
4. What if you had 100 services?

**Discussion Points**:
- How does async help with scalability?
- What are the limitations?
- When would you need more advanced patterns (rate limiting, retries)?

---

## 🎓 Comparison to Previous Examples

| Feature | hello-agent | calculator-agent | async-tools-agent |
|---------|-------------|------------------|-------------------|
| **Tools** | 1 simple tool | 5 math tools | 1 async tool |
| **Concurrency** | N/A | Sequential | Concurrent |
| **I/O Operations** | None | None | Network requests |
| **Error Handling** | Basic | Math errors | Network errors |
| **Performance Focus** | No | No | **Yes - timing matters** |
| **Complexity** | ⭐ | ⭐⭐ | ⭐⭐ |

### What's New in This Example?

1. **Async/Await Syntax**: First async tool in the series
2. **Concurrent Execution**: Multiple operations at once
3. **External I/O**: Real network requests
4. **Performance Metrics**: Timing and efficiency
5. **Partial Failure Handling**: Some requests can fail while others succeed

### Building on Previous Concepts

- **From hello-agent**: Still using `@tool` decorator and Agent class
- **From calculator-agent**: Still returning structured dictionaries with metadata
- **New addition**: Async patterns for I/O-bound operations

---

## 🚀 Next Steps

### Immediate Next Steps
1. Deploy and test the agent with various URL combinations
2. Monitor the performance differences between 1, 5, 10, and 20 URLs
3. Try deliberately causing timeouts to see error handling
4. Experiment with different types of APIs

### Extend This Example

**Idea 1: Add Retry Logic**
```python
async def fetch_with_retry(session, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await fetch_one(session, url)
        except:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

**Idea 2: Add Response Time Tracking**
Track how long each individual request takes and identify the slowest endpoints.

**Idea 3: Add Content Type Detection**
Parse Content-Type headers and handle JSON, HTML, XML differently.

**Idea 4: Add Caching**
Cache responses for a configurable duration to avoid redundant requests.

### What's Next in the Learning Path?

**Next Example**: `structured-data-agent` (Example 5)
- Complex data structures and type hints
- Pydantic models for validation
- Rich data passing between tools
- Advanced return formats

**Why This Order Makes Sense**:
You now understand async operations. Next, you'll learn to handle complex data structures, which you can then combine with async for powerful data processing agents.

---

## 📖 Additional Resources

### Understanding Async/Await
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [aiohttp documentation](https://docs.aiohttp.org/)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)

### When to Use Async
- **Good fit**: API calls, web scraping, database queries, file operations
- **Poor fit**: Mathematical computations, image processing, video encoding
- **Rule**: If you're waiting more than computing, use async

### Performance Considerations
- Async shines with **many** concurrent operations (10+)
- For 1-2 operations, the overhead isn't worth it
- Network latency is the main bottleneck async solves
- CPU-bound work needs multiprocessing, not async

---

## 🐛 Troubleshooting

### "Cannot connect to host" errors
- Check if the URL is correct (include https://)
- Verify network connectivity
- Some sites may block automated requests

### "SSL certificate verification failed"
- Some sites have SSL issues
- The tool uses standard verification - this is intentional
- In production, you might add certificate handling

### Slow performance
- Check your network connection
- Some URLs may be genuinely slow
- Timeout is set to 10 seconds per request
- Consider reducing timeout for faster failure detection

### "Event loop is closed" error
- This shouldn't happen with the NCP SDK
- If you see it, you're likely testing outside the agent context
- The SDK manages the event loop automatically

---

**Congratulations!** You now understand async tools and concurrent operations. This is a critical skill for building efficient, production-ready agents that interact with external systems.

Ready for more? Move on to **Example 5: structured-data-agent** to learn about complex data structures and type safety!
