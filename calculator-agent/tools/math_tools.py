"""Mathematical operation tools for the calculator agent.

This module provides basic arithmetic operations that can be used
by the AI agent to perform calculations.
"""

from ncp import tool


@tool
def add(a: float, b: float) -> dict:
    """Add two numbers together.

    This tool performs addition of two numbers and returns the result.
    Use this when you need to find the sum of two values.

    Args:
        a: The first number to add
        b: The second number to add

    Returns:
        A dictionary containing the operation details and result

    Examples:
        >>> add(5, 3)
        {"operation": "addition", "operands": [5, 3], "result": 8}

        >>> add(10.5, 20.3)
        {"operation": "addition", "operands": [10.5, 20.3], "result": 30.8}
    """
    result = a + b
    return {
        "operation": "addition",
        "operands": [a, b],
        "result": result,
        "expression": f"{a} + {b} = {result}"
    }


@tool
def subtract(a: float, b: float) -> dict:
    """Subtract one number from another.

    This tool performs subtraction (a - b) and returns the result.
    Use this when you need to find the difference between two values.

    Args:
        a: The number to subtract from (minuend)
        b: The number to subtract (subtrahend)

    Returns:
        A dictionary containing the operation details and result

    Examples:
        >>> subtract(10, 3)
        {"operation": "subtraction", "operands": [10, 3], "result": 7}

        >>> subtract(5.5, 2.3)
        {"operation": "subtraction", "operands": [5.5, 2.3], "result": 3.2}
    """
    result = a - b
    return {
        "operation": "subtraction",
        "operands": [a, b],
        "result": result,
        "expression": f"{a} - {b} = {result}"
    }


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

    Examples:
        >>> multiply(4, 5)
        {"operation": "multiplication", "operands": [4, 5], "result": 20}

        >>> multiply(2.5, 3)
        {"operation": "multiplication", "operands": [2.5, 3], "result": 7.5}
    """
    result = a * b
    return {
        "operation": "multiplication",
        "operands": [a, b],
        "result": result,
        "expression": f"{a} × {b} = {result}"
    }


@tool
def divide(a: float, b: float) -> dict:
    """Divide one number by another.

    This tool performs division (a / b) and returns the result.
    Use this when you need to find the quotient of two values.
    Handles division by zero gracefully with an error message.

    Args:
        a: The dividend (number to be divided)
        b: The divisor (number to divide by)

    Returns:
        A dictionary containing the operation details and result,
        or an error message if division by zero is attempted

    Examples:
        >>> divide(10, 2)
        {"operation": "division", "operands": [10, 2], "result": 5.0}

        >>> divide(15, 4)
        {"operation": "division", "operands": [15, 4], "result": 3.75}

        >>> divide(10, 0)
        {"operation": "division", "error": "Cannot divide by zero"}
    """
    if b == 0:
        return {
            "operation": "division",
            "operands": [a, b],
            "error": "Cannot divide by zero",
            "expression": f"{a} ÷ {b} = undefined"
        }

    result = a / b
    return {
        "operation": "division",
        "operands": [a, b],
        "result": result,
        "expression": f"{a} ÷ {b} = {result}"
    }


@tool
def power(base: float, exponent: float) -> dict:
    """Raise a number to a power (exponentiation).

    This tool calculates base raised to the power of exponent (base^exponent).
    Use this for exponential calculations, squares, cubes, and roots.

    Args:
        base: The base number
        exponent: The power to raise the base to

    Returns:
        A dictionary containing the operation details and result,
        or an error message if the operation is invalid

    Examples:
        >>> power(2, 3)
        {"operation": "exponentiation", "operands": [2, 3], "result": 8}

        >>> power(5, 2)
        {"operation": "exponentiation", "operands": [5, 2], "result": 25}

        >>> power(16, 0.5)
        {"operation": "exponentiation", "operands": [16, 0.5], "result": 4.0}

    Note:
        - Negative bases with fractional exponents may result in complex numbers
        - Use exponent of 0.5 for square root, 0.333... for cube root, etc.
    """
    try:
        result = base ** exponent
        return {
            "operation": "exponentiation",
            "operands": [base, exponent],
            "result": result,
            "expression": f"{base}^{exponent} = {result}"
        }
    except Exception as e:
        return {
            "operation": "exponentiation",
            "operands": [base, exponent],
            "error": f"Cannot calculate {base}^{exponent}: {str(e)}",
            "expression": f"{base}^{exponent} = error"
        }
