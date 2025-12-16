"""Mathematical tools for the math specialist agent."""

from ncp import tool


@tool
def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression.

    Safely evaluates basic arithmetic expressions.

    Args:
        expression: A mathematical expression like "2 + 3 * 4"

    Returns:
        The result of the calculation
    """
    try:
        # Only allow safe mathematical operations
        allowed_chars = set("0123456789+-*/().^ ")
        if not all(c in allowed_chars for c in expression):
            return {"error": "Invalid characters in expression"}

        # Replace ^ with ** for exponentiation
        safe_expr = expression.replace("^", "**")
        result = eval(safe_expr)
        return {
            "expression": expression,
            "result": result,
            "formatted": f"{expression} = {result}"
        }
    except Exception as e:
        return {"error": f"Could not evaluate: {str(e)}"}


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert between common units.

    Args:
        value: The numeric value to convert
        from_unit: Source unit (e.g., "km", "miles", "kg", "lbs")
        to_unit: Target unit

    Returns:
        The converted value
    """
    conversions = {
        ("km", "miles"): 0.621371,
        ("miles", "km"): 1.60934,
        ("kg", "lbs"): 2.20462,
        ("lbs", "kg"): 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("meters", "feet"): 3.28084,
        ("feet", "meters"): 0.3048,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        factor = conversions[key]
        if callable(factor):
            result = factor(value)
        else:
            result = value * factor
        return {
            "original": f"{value} {from_unit}",
            "converted": f"{result:.4f} {to_unit}",
            "result": result
        }

    return {"error": f"Cannot convert from {from_unit} to {to_unit}"}
