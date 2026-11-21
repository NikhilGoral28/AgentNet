"""Example using Google Gemini with AgentNet."""

from pydantic import BaseModel

from agentnet import Extractor, Summarizer
from agentnet.providers.adapters.fake import FakeProviderAdapter

# In production with live API credentials:
# export GEMINI_API_KEY="AIzaSy..."  (or GOOGLE_API_KEY)
# agent = Summarizer(model="gemini/gemini-2.5-flash")

print("Initializing Gemini-backed agents...")

# Demonstrating Gemini model configuration
mock_gemini_adapter = FakeProviderAdapter(
    default_response="Gemini Summary: Multimodal artificial intelligence synthesizes text, vision, and audio natively."
)

agent = Summarizer(
    model="gemini/gemini-2.5-flash",
    provider_adapter=mock_gemini_adapter,
)

result = agent.run(
    text="Multimodal artificial intelligence represents a paradigm shift where models process text, images, and audio natively in unified representations.",
    style="concise",
)

print("\nGemini Agent Result:")
print(f"Model:    {result.model}")
print(f"Output:   {result.output}")
print(f"Duration: {result.duration:.3f}s")


# Structured Extraction with Gemini
class KeyFinding(BaseModel):
    architecture: str
    benefit: str


mock_extractor_adapter = FakeProviderAdapter(
    response_fn=lambda req: {
        "architecture": "Native Multimodal Transformer",
        "benefit": "Cross-modality contextual reasoning",
    }
)

extractor = Extractor(
    model="gemini/gemini-2.5-flash",
    output_schema=KeyFinding,
    provider_adapter=mock_extractor_adapter,
)

extraction_res = extractor.run(
    text="Native multimodal architectures enable end-to-end reasoning across audio, video, and text."
)
finding: KeyFinding = extraction_res.output
print(f"\nGemini Structured Extraction: {finding.architecture} -> {finding.benefit}")
