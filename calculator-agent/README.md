# Calculator Agent

**Learn how multiple tools work together through multi-step reasoning**

This example demonstrates how AI agents can combine multiple tools to solve complex problems. You'll learn how the LLM orchestrates different operations, handles errors gracefully, and breaks down complex calculations into manageable steps.

---

## 🎯 What You'll Learn

By the end of this example, you'll understand:

- ✅ **Multiple Tools**: How to create agents with several related tools
- ✅ **Multi-Step Reasoning**: How LLMs chain tool calls to solve complex problems
- ✅ **Error Handling**: How to handle edge cases (like division by zero)
- ✅ **Structured Returns**: How tools return rich data structures
- ✅ **Tool Organization**: How to organize related tools in modules
- ✅ **Type Flexibility**: How to use float types for numeric operations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ installed
- NCP SDK installed (`pip install ncp-sdk`)
- Completed the [hello-agent](../hello-agent) example (recommended)

### Installation

```bash
# Navigate to this example
cd calculator-agent

# Install dependencies
pip install -r requirements.txt

# Validate the project
ncp validate .
```

---

## 📁 Project Structure

```
calculator-agent/
├── README.md              # This file - tutorial and guide
├── ncp.toml              # Project configuration
├── requirements.txt      # Python dependencies
├── agents/
│   ├── __init__.py
│   └── main_agent.py    # Agent definition with 5 tools
└── tools/
    ├── __init__.py
    └── math_tools.py    # All mathematical operations
```

---

## 🔧 The Tools

This agent has **5 mathematical tools**:

### 1. Addition (`add`)

```python
add(a: float, b: float) -> dict
```

Adds two numbers together. Returns the sum with operation details.

**Example**: `add(15, 27)` → `{"result": 42, "expression": "15 + 27 = 42"}`

### 2. Subtraction (`subtract`)

```python
subtract(a: float, b: float) -> dict
```

Subtracts the second number from the first.

**Example**: `subtract(50, 23)` → `{"result": 27, "expression": "50 - 23 = 27"}`

### 3. Multiplication (`multiply`)

```python
multiply(a: float, b: float) -> dict
```

Multiplies two numbers together.

**Example**: `multiply(6, 7)` → `{"result": 42, "expression": "6 × 7 = 42"}`

### 4. Division (`divide`)

```python
divide(a: float, b: float) -> dict
```

Divides the first number by the second. **Handles division by zero gracefully**.

**Example**: `divide(84, 2)` → `{"result": 42.0, "expression": "84 ÷ 2 = 42.0"}`

**Error Handling**: `divide(10, 0)` → `{"error": "Cannot divide by zero"}`

### 5. Exponentiation (`power`)

```python
power(base: float, exponent: float) -> dict
```

Raises a number to a power. Can also calculate roots using fractional exponents.

**Examples**:

- `power(2, 10)` → `{"result": 1024, "expression": "2^10 = 1024"}`
- `power(16, 0.5)` → `{"result": 4.0, "expression": "16^0.5 = 4.0"}` (square root)

---

## 🎬 Example Interactions

### Basic Calculation

```
You: What is 25 + 17?

Agent: Let me calculate that for you.
[Uses tool: add(25, 17)]
The sum of 25 and 17 is 42.
```

### Multi-Step Calculation

```
You: Calculate (10 + 5) × 3

Agent: I'll break this down step by step:

Step 1: First, let me add 10 and 5
[Uses tool: add(10, 5)]
10 + 5 = 15

Step 2: Now multiply the result by 3
[Uses tool: multiply(15, 3)]
15 × 3 = 45

The final answer is 45.
```

### Complex Calculation with Tax

```
You: Calculate the total cost: $45.99 + $32.50 + 15% tax

Agent: Let me calculate the total with tax:

Step 1: Add the two prices
[Uses tool: add(45.99, 32.50)]
$45.99 + $32.50 = $78.49

Step 2: Calculate 15% of the subtotal
[Uses tool: multiply(78.49, 0.15)]
15% of $78.49 = $11.77

Step 3: Add the tax to get the final total
[Uses tool: add(78.49, 11.77)]
$78.49 + $11.77 = $90.26

The total cost including 15% tax is $90.26.
```

### Error Handling

```
You: What's 100 divided by 0?

Agent: Let me attempt that division.
[Uses tool: divide(100, 0)]

I cannot divide 100 by 0 because division by zero is mathematically undefined.
It's an invalid operation that would result in infinity.

Is there a different calculation you'd like me to perform?
```

### Using Powers

```
You: What's 2 to the power of 10?

Agent: Let me calculate that.
[Uses tool: power(2, 10)]
2^10 = 1024

Two raised to the power of ten equals 1,024.
```

---

## 💡 The "Aha!" Moment

Try this query to see multi-step reasoning in action:

```
You: "I need to split a $150 restaurant bill among 4 people,
      then add a 20% tip per person. How much does each person pay?"
```

Watch the agent:

1. **Divide** $150 by 4 → $37.50 per person (before tip)
2. **Multiply** $37.50 by 0.20 → $7.50 tip per person
3. **Add** $37.50 + $7.50 → $45.00 final amount per person

The agent **reasons through the problem**, choosing the right tools in the right order!

---

## 🧠 Key Concepts

### 1. Multiple Tools = More Capabilities

Instead of one tool, this agent has five. The LLM decides which tool(s) to use based on the user's question.

```python
agent = Agent(
    name="CalculatorAgent",
    tools=[add, subtract, multiply, divide, power]  # 5 tools!
)
```

### 2. Multi-Step Reasoning

For complex problems, the LLM breaks them into steps:

**Problem**: `(10 + 5) × 3`

**LLM's Reasoning**:

1. "I need to add first: 10 + 5"
2. "Then multiply the result by 3"

**Tool Calls**:

1. `add(10, 5)` → Result: 15
2. `multiply(15, 3)` → Result: 45

### 3. Structured Data Returns

Each tool returns a **dictionary** with rich information:

```python
{
    "operation": "multiplication",
    "operands": [15, 3],
    "result": 45,
    "expression": "15 × 3 = 45"
}
```

This gives the LLM context about:

- What operation was performed
- What the inputs were
- What the result is
- A human-readable expression

### 4. Error Handling

The `divide` tool checks for division by zero:

```python
if b == 0:
    return {
        "operation": "division",
        "error": "Cannot divide by zero",
        "expression": f"{a} ÷ {b} = undefined"
    }
```

**Why this matters**: The tool doesn't crash. Instead, it returns error information that the LLM can explain to the user in natural language.

### 5. Type Hints with Floats

All tools use `float` for numeric parameters:

```python
def add(a: float, b: float) -> dict:
```

**Why floats?**

- Handles both integers and decimals
- More flexible for real-world calculations
- Python automatically converts `5` to `5.0`

---

## 📚 Code Deep Dive

### Tool Implementation Pattern

Look at how the `multiply` tool is structured:

```python
@tool
def multiply(a: float, b: float) -> dict:
    """Multiply two numbers together.

    This tool performs multiplication of two numbers and returns the result.
    Use this when you need to find the product of two values.

    Args:
        a: The first number to multiply
        b: The second number to multiply

    Returns:
        A dictionary containing the operation details and result
    """
    result = a * b
    return {
        "operation": "multiplication",
        "operands": [a, b],
        "result": result,
        "expression": f"{a} × {b} = {result}"
    }
```

**Key elements**:

1. **`@tool` decorator** - Makes it available to the agent
2. **Type hints** - `a: float, b: float -> dict`
3. **Comprehensive docstring** - The LLM reads this!
4. **Structured return** - Rich data, not just a number

### Agent Instructions

The agent's instructions tell it **how to use the tools**:

```python
instructions="""You are a helpful calculator assistant with access to mathematical tools.

When solving problems:
1. Break down complex calculations into individual steps
2. Use the appropriate tool for each operation
3. Show your work by explaining each step
4. Present the final answer clearly
5. Handle errors gracefully (like division by zero)"""
```

**This is crucial!** Good instructions guide the agent's behavior.

---

## 🔬 Try It Yourself

### Experiment 1: Simple Operations

```
- "What's 123 + 456?"
- "Subtract 89 from 200"
- "Multiply 12 by 15"
```

### Experiment 2: Multi-Step Problems

```
- "Calculate (20 + 30) ÷ 5"
- "What's 10 squared?"
- "Find the square root of 144" (Hint: power(144, 0.5))
```

### Experiment 3: Real-World Scenarios

```
- "I earned $2,500 this month. If I save 20%, how much do I save?"
- "A recipe calls for 2.5 cups of flour. I want to triple it. How much flour do I need?"
- "Calculate compound interest: $1000 at 5% for 3 years" (Hint: 1000 × 1.05^3)
```

### Experiment 4: Error Cases

```
- "Divide 50 by 0"
- "What's 10 ÷ 0?"
```

See how the agent handles errors gracefully!

---

## 🎓 What Makes This Different from hello-agent?

| Feature           | hello-agent      | calculator-agent                           |
| ----------------- | ---------------- | ------------------------------------------ |
| Number of tools   | 1 (say_hello)    | 5 (add, subtract, multiply, divide, power) |
| Tool coordination | Single tool call | Multi-step reasoning                       |
| Error handling    | None needed      | Division by zero handling                  |
| Return type       | Simple string    | Structured dictionary                      |
| Complexity        | Beginner         | Intermediate                               |

---

## 🚀 Next Steps

### Modify This Agent

Try these extensions:

1. **Add more tools**:

   ```python
   @tool
   def modulo(a: float, b: float) -> dict:
       """Calculate remainder after division."""
       pass

   @tool
   def percentage(value: float, percent: float) -> dict:
       """Calculate percentage of a value."""
       pass
   ```

2. **Add validation**:

   ```python
   if a < 0 and exponent != int(exponent):
       return {"error": "Cannot raise negative number to fractional power"}
   ```

3. **Add more sophisticated operations**:
   - Factorial
   - Square root (as a dedicated function)
   - Trigonometry (sin, cos, tan)

### Deploy It

```bash
# Package the agent
ncp package .

# Authenticate with platform
ncp authenticate

# Deploy
ncp deploy calculator-agent.ncp

# Test in playground
ncp playground --agent calculator-agent
```
