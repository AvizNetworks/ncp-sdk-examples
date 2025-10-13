# Hello Agent - Your First NCP SDK Agent

**A simple but powerful example demonstrating how AI agents combine their built-in knowledge with custom tools.**

---

## 🎯 What This Example Teaches

This hello-agent example is designed to teach you:

1. **Tool Creation**: How to create custom tools using the `@tool` decorator
2. **LLM Knowledge + Tools**: How agents combine their built-in knowledge with your custom tools
3. **Type Hints & Docstrings**: How they help the LLM understand and use your tools effectively
4. **Project Structure**: How to organize an NCP SDK project

### The "Aha!" Moment

The magic happens when you ask: **"Say hello to the last 5 US presidents"**

- ✅ The agent **uses its knowledge** to identify: Joe Biden, Donald Trump, Barack Obama, George W. Bush, Bill Clinton
- ✅ Then **calls your custom tool** 5 times to greet each president
- ✅ Combines everything into a natural response

This demonstrates that AI agents are **knowledge + tools working together**!

---

## 📁 Project Structure

```
hello-agent/
├── README.md                  # This file - your guide
├── ncp.toml                   # Project configuration
├── requirements.txt           # Python dependencies
├── agents/
│   ├── __init__.py           # Makes agents a Python package
│   └── main_agent.py         # 🎯 Your agent definition
└── tools/
    ├── __init__.py           # Makes tools a Python package
    └── greeting_tools.py     # 🔧 Your custom tool
```

### Key Files Explained

| File                      | Purpose                                                          |
| ------------------------- | ---------------------------------------------------------------- |
| `ncp.toml`                | Project metadata, version, entry point configuration             |
| `agents/main_agent.py`    | Defines your agent's behavior, instructions, and available tools |
| `tools/greeting_tools.py` | Contains your custom tools (functions decorated with `@tool`)    |
| `requirements.txt`        | Python packages your agent needs                                 |

---

## 🔧 The Tool: `say_hello`

Let's look at the tool in `tools/greeting_tools.py`:

```python
from ncp import tool

@tool
def say_hello(name: str) -> str:
    """Say hello to someone by name.

    This tool generates a personalized greeting for any person.
    Use this tool after identifying who needs to be greeted.

    Args:
        name: The full name of the person to greet (e.g., "John Doe")

    Returns:
        A friendly greeting message for the specified person
    """
    return f"Hello, {name}! Nice to meet you!"
```

### Breaking It Down

1. **`@tool` Decorator**:
   - Converts a regular Python function into an agent tool
   - Automatically generates a schema that the LLM can understand
   - Handles async execution and error handling

2. **Type Hints** (`name: str -> str`):
   - Tell the LLM what type of input the tool expects
   - Help generate accurate tool schemas
   - Enable validation before tool execution

3. **Docstring**:
   - **First line**: Brief description the LLM sees
   - **Args section**: Explains each parameter
   - **Returns section**: Describes the output
   - **The LLM reads this!** Write docstrings as if explaining to a colleague

4. **Implementation**:
   - Simple Python logic
   - Returns a string (matches type hint)
   - Could be anything: API calls, database queries, file operations, etc.

### What Makes a Good Tool?

✅ **DO**:

- Write clear, descriptive docstrings
- Use type hints for all parameters
- Return structured data (dicts, lists, strings)
- Handle errors gracefully
- Keep tools focused (single responsibility)

❌ **AVOID**:

- Vague docstrings like "does something"
- Missing type hints
- Raising unhandled exceptions
- Doing too many things in one tool

---

## 🤖 The Agent: `HelloAgent`

Let's look at `agents/main_agent.py`:

```python
from ncp import Agent, LLMConfig
from tools.greeting_tools import say_hello

agent = Agent(
    name="HelloAgent",
    description="A friendly greeting assistant that uses AI knowledge and tools",
    instructions="You are a friendly greeting assistant. Your goal is to greet people by name.",
    tools=[say_hello]
)
```

### Agent Configuration Explained

| Parameter      | Purpose                            | Example                  |
| -------------- | ---------------------------------- | ------------------------ |
| `name`         | Unique identifier for your agent   | `"HelloAgent"`           |
| `description`  | Brief summary of agent's purpose   | Used in agent listings   |
| `instructions` | System prompt that guides behavior | The most important part! |
| `tools`        | List of available tools            | `[say_hello]`            |

### The Power of Good Instructions

The `instructions` field is where the magic happens. Notice how we:

1. **Set Context**: "You are a friendly greeting assistant"
2. **Explain Available Tools**: "You have access to a tool called 'say_hello'"
3. **Provide Workflow**: Step-by-step guide on how to use tools
4. **Give Examples**: Concrete scenarios showing expected behavior
5. **Encourage Knowledge Use**: "Use your knowledge to identify... then call the tool"

**This is the key to effective agents**: Clear instructions that guide the LLM to combine its knowledge with your tools.

---

## 🚀 Try It Out

### Setup

```bash
# Navigate to hello-agent directory
cd hello-agent

# Install dependencies
pip install -r requirements.txt

# Validate the project
ncp validate .
```

### Example Interactions

#### Example 1: Simple Greeting

**You**: Say hello to Jim

**Agent**:

```
I'll greet Jim for you!
[calls say_hello("Jim")]
Hello, Jim! Nice to meet you!
```

**What Happened**: Simple and straightforward - agent used the tool with the name you provided.

---

#### Example 2: The Magic - Using LLM Knowledge

**You**: Say hello to the last 5 US presidents

**Agent**:

```
I'll greet the last 5 US presidents for you!

[calls say_hello("Joe Biden")]
Hello, Joe Biden! Nice to meet you!

[calls say_hello("Donald Trump")]
Hello, Donald Trump! Nice to meet you!

[calls say_hello("Barack Obama")]
Hello, Barack Obama! Nice to meet you!

[calls say_hello("George W. Bush")]
Hello, George W. Bush! Nice to meet you!

[calls say_hello("Bill Clinton")]
Hello, Bill Clinton! Nice to meet you!

I've greeted all five of the most recent US presidents!
```

**What Happened** ✨:

1. Agent **used its knowledge** to identify the last 5 presidents
2. Agent **called your tool** 5 times with correct full names
3. Agent **presented results** naturally

This is the power of combining LLM knowledge with custom tools!

---

#### Example 3: More Complex Queries

**You**: Greet the founders of Apple

**Agent**:

```
I'll greet the founders of Apple Inc.!

[calls say_hello("Steve Jobs")]
Hello, Steve Jobs! Nice to meet you!

[calls say_hello("Steve Wozniak")]
Hello, Steve Wozniak! Nice to meet you!

[calls say_hello("Ronald Wayne")]
Hello, Ronald Wayne! Nice to meet you!

I've greeted all three founders of Apple!
```

**What Happened**: Agent knew there were 3 founders (including the lesser-known Ronald Wayne), then used your tool to greet each.

---

## 🔍 How It Works

### Execution Flow

```
1. User Input
   "Say hello to the last 5 US presidents"

2. Agent Analyzes Request
   - Reads instructions
   - Understands task: need to greet specific people
   - Realizes it needs to identify presidents first

3. Agent Uses Built-in Knowledge
   - Accesses training data about US presidents
   - Identifies: Biden, Trump, Obama, Bush, Clinton

4. Agent Plans Tool Calls
   - Decides to call say_hello 5 times
   - Prepares parameters for each call

5. Tool Execution (Automatic)
   - NCP SDK executes each say_hello call
   - Collects results

6. Agent Synthesizes Response
   - Combines tool outputs
   - Presents results naturally
   - May add context or explanation
```

### The Agent's Perspective

When you ask "Say hello to the last 5 US presidents", the agent:

1. **Sees your request** in context
2. **Reads its instructions** to understand its role
3. **Knows about US presidents** from training data
4. **Sees tool schema** for `say_hello(name: str) -> str`
5. **Makes a plan**: Identify presidents → Call tool for each → Present results
6. **Executes plan**: Makes 5 tool calls
7. **Returns response**: Combined, natural output

---

## 🎓 Key Takeaways

### What You Learned

1. **Tools are Just Python Functions**
   - Add `@tool` decorator
   - Use type hints
   - Write good docstrings
   - That's it!

2. **Agents Combine Knowledge + Tools**
   - LLMs have vast knowledge
   - Tools provide actions
   - Instructions guide how to combine them

3. **Instructions are Critical**
   - They shape agent behavior
   - Examples help the LLM understand
   - Clear workflows prevent confusion

4. **Type Hints Matter**
   - Help generate accurate schemas
   - Enable validation
   - Guide the LLM on usage

5. **Docstrings are for the LLM**
   - Write them clearly
   - Explain when to use the tool
   - Describe parameters and returns

### Design Patterns You Saw

- **Single Responsibility**: `say_hello` does one thing well
- **Clear Naming**: Function name explains what it does
- **Structured Output**: Returns a simple, predictable string
- **Graceful Execution**: No error handling needed for this simple case

---

## 🚀 Next Steps

### Enhance This Agent

Try modifying hello-agent to practice:

1. **Add a New Tool**:

   ```python
   @tool
   def say_goodbye(name: str) -> str:
       """Say goodbye to someone."""
       return f"Goodbye, {name}! Have a great day!"
   ```

   Add it to `tools=[say_hello, say_goodbye]`

2. **Make It More Personal**:

   ```python
   @tool
   def personalized_greeting(name: str, time_of_day: str = "day") -> str:
       """Generate time-appropriate greeting."""
       greetings = {
           "morning": f"Good morning, {name}!",
           "afternoon": f"Good afternoon, {name}!",
           "evening": f"Good evening, {name}!"
       }
       return greetings.get(time_of_day, f"Hello, {name}!")
   ```

3. **Add Error Handling**:
   ```python
   @tool
   def safe_greeting(name: str) -> dict:
       """Greet someone with error handling."""
       try:
           if not name or not name.strip():
               return {"success": False, "error": "Name cannot be empty"}
           return {"success": True, "message": f"Hello, {name}!"}
       except Exception as e:
           return {"success": False, "error": str(e)}
   ```

---
