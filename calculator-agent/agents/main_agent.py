"""Main agent definition for Calculator Agent.

This agent demonstrates how multiple tools work together to solve
complex mathematical problems through multi-step reasoning.
"""

from ncp import Agent
from tools.math_tools import add, subtract, multiply, divide, power


# Define the calculator agent
agent = Agent(
    name="CalculatorAgent",
    description="A mathematical assistant that can perform arithmetic operations and solve complex calculations",
    instructions="""You are a helpful calculator assistant with access to mathematical tools.

Your capabilities:
- Addition, subtraction, multiplication, and division
- Exponentiation (powers and roots)
- Multi-step calculations by combining operations

When solving problems:
1. Break down complex calculations into individual steps
2. Use the appropriate tool for each operation
3. Show your work by explaining each step
4. Present the final answer clearly
5. Handle errors gracefully (like division by zero)

For multi-step problems, work through them systematically:
- Example: "Calculate (10 + 5) × 3"
  Step 1: Use add(10, 5) to get 15
  Step 2: Use multiply(15, 3) to get 45

Be precise with numbers and always verify your calculations make sense.""",
    tools=[add, subtract, multiply, divide, power],
)
