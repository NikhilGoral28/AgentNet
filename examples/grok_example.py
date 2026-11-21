"""Example using xAI Grok with AgentNet."""

from pydantic import BaseModel

from agentnet import Extractor, Summarizer
from agentnet.providers.adapters.fake import FakeProviderAdapter

# In production with live API credentials:
# export XAI_API_KEY="xai-..."
# agent = Summarizer(model="grok/grok-2")

print("Initializing Grok-backed agents...")

# Demonstrating Grok model configuration
mock_grok_adapter = FakeProviderAdapter(
    default_response="Grok Summary: Quantum computing leverages superposition and entanglement for exponential parallelism."
)

agent = Summarizer(
    model="grok/grok-2",
    provider_adapter=mock_grok_adapter,
)

result = agent.run(
    text="Quantum computing is an emerging technology that harnesses the laws of quantum mechanics to solve problems too complex for classical computers.",
    style="concise",
)

print("\nGrok Agent Result:")
print(f"Model:    {result.model}")
print(f"Output:   {result.output}")
print(f"Duration: {result.duration:.3f}s")

# Structured Extraction with Grok
class ResearchFinding(BaseModel):
    topic: str
    significance: str

mock_extractor_adapter = FakeProviderAdapter(
    response_fn=lambda req: {
        "topic": "Quantum Mechanics",
        "significance": "Exponential algorithmic speedup",
    }
)

extractor = Extractor(
    model="grok/grok-2",
    output_schema=ResearchFinding,
    provider_adapter=mock_extractor_adapter,
)

extraction_res = extractor.run(text="Quantum mechanics enables exponential speedups.")
finding: ResearchFinding = extraction_res.output
print(f"\nGrok Structured Extraction: {finding.topic} -> {finding.significance}")
