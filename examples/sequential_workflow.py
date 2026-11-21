"""Sequential workflow example using AgentNet."""

from agentnet import EmailWriter, SequentialWorkflow, Summarizer
from agentnet.providers.adapters.fake import FakeProviderAdapter

# Create adapters for demonstration
summary_adapter = FakeProviderAdapter(
    default_response="Key updates: Q3 target exceeded by 18%, new platform deployed."
)
email_adapter = FakeProviderAdapter(
    default_response=(
        "Subject: Executive Brief - Q3 Milestones\n\n"
        "Dear Leadership,\n\n"
        "Our Q3 targets were exceeded by 18% with the successful deployment of the new platform.\n\n"
        "Best regards,\nOperations Team"
    )
)

summarizer = Summarizer(model="openai/gpt-4.1", provider_adapter=summary_adapter)
email_writer = EmailWriter(model="openai/gpt-4.1", provider_adapter=email_adapter)

workflow = SequentialWorkflow(
    steps=[
        ("summary", summarizer),
        ("email", email_writer),
    ],
    step_mappings={
        "email": lambda state: {
            "purpose": state["summary"].output,
            "recipient": "Leadership Team",
            "tone": "executive",
        }
    },
)

result = workflow.run(text="Raw operations report for Q3 with detailed metrics...")
print("Final Workflow Output:\n")
print(result.output)
print(f"\nTotal Pipeline Tokens: {result.usage.total_tokens}")
print(f"Executed Steps: {list(result.metadata['steps'].keys())}")
