"""Basic summarization example using AgentNet."""

from agentnet import Summarizer
from agentnet.providers.adapters.fake import FakeProviderAdapter

# For live usage: agent = Summarizer(model="openai/gpt-4.1")
# Here we use FakeProviderAdapter for a self-contained demonstration
adapter = FakeProviderAdapter(
    default_response=(
        "Summary:\n"
        "- AgentNet is a production-oriented AI agent library.\n"
        "- It provides predefined typed agents with schema validation.\n"
        "- Supports both synchronous and asynchronous execution."
    )
)

agent = Summarizer(model="openai/gpt-4.1", provider_adapter=adapter)

result = agent.run(
    text=(
        "AgentNet is a reusable Python AI agent framework designed for production applications. "
        "It provides developers with typed agent classes, schema validation with Pydantic, "
        "reusable tools, and workflow execution capabilities."
    ),
    style="bullet_points",
    max_words=100,
)

print("Agent Output:")
print(result.output)
print("\nExecution Metadata:")
print(f"Model: {result.model}")
print(f"Duration: {result.duration:.3f}s")
print(f"Tokens: {result.usage.total_tokens} (prompt: {result.usage.prompt_tokens}, completion: {result.usage.completion_tokens})")
print(f"Run ID: {result.run_id}")
