"""Tool definition and execution example with AgentNet."""

from agentnet import Tool


def calculate_total(price: float, quantity: int) -> float:
    """Calculate price multiplied by quantity."""
    return price * quantity


# Define Tool with automatic schema inference
calculator = Tool(
    name="calculate_total",
    description="Calculate price multiplied by quantity",
    function=calculate_total,
)

# Tool execution with argument validation
result = calculator.execute({"price": 24.50, "quantity": 4})
print(f"Calculation Result: ${result:.2f}")

# JSON schema definition for model calling
print("\nGenerated Tool Schema for Model Providers:")
import json

print(json.dumps(calculator.to_dict(), indent=2))
