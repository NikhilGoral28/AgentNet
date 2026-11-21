"""Structured extraction example using AgentNet and Pydantic."""

from pydantic import BaseModel

from agentnet import Extractor
from agentnet.providers.adapters.fake import FakeProviderAdapter


class Contact(BaseModel):
    name: str
    email: str | None = None
    organization: str | None = None


# Using FakeProviderAdapter for self-contained demonstration without requiring an API key
mock_adapter = FakeProviderAdapter(
    response_fn=lambda req: {
        "name": "Priya Shah",
        "email": "priya@example.com",
        "organization": "Acme Ltd.",
    }
)

extractor = Extractor(
    model="openai/gpt-4.1",
    output_schema=Contact,
    provider_adapter=mock_adapter,
)

result = extractor.run(
    text="Contact Priya Shah at priya@example.com, Acme Ltd."
)

contact: Contact = result.output

print(f"Extracted Name:         {contact.name}")
print(f"Extracted Email:        {contact.email}")
print(f"Extracted Organization: {contact.organization}")
print(f"Validated Pydantic:     {type(contact).__name__}")
