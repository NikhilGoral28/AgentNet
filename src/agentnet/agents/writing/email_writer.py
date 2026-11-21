"""EmailWriter agent implementation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import EMAIL_WRITER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class EmailDraft(BaseModel):
    """Structured email draft model."""

    subject: str
    body: str


class EmailWriter(BaseAgent[Any]):
    """Drafts contextual emails based on purpose, recipient, and tone."""

    def __init__(self, model: str | None = None, **kwargs: Any) -> None:
        super().__init__(model=model, **kwargs)
        self._system_template = PromptTemplate(EMAIL_WRITER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        purpose: str,
        recipient: str,
        tone: str,
        length: str,
        include_subject: bool,
    ) -> list[ChatMessage]:
        if not purpose or not purpose.strip():
            raise ValidationError("EmailWriter requires a non-empty 'purpose'.")
        if not recipient or not recipient.strip():
            raise ValidationError("EmailWriter requires a non-empty 'recipient'.")

        format_inst = (
            "Include 'Subject: <subject>' on the first line, followed by the email body."
            if include_subject
            else "Write only the email body without a subject line."
        )

        system_content = self._system_template.format(
            recipient=recipient,
            purpose=purpose,
            tone=tone,
            length=length,
            format_instruction=format_inst,
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Please draft an email to recipient '{recipient}' regarding purpose:\n<untrusted_user_input>\n{purpose}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        purpose: str,
        recipient: str = "Recipient",
        tone: str = "professional",
        length: str = "concise",
        include_subject: bool = True,
        as_structured: bool = False,
        **kwargs: Any,
    ) -> AgentResult[Any]:
        """Execute email draft generation synchronously."""
        messages = self._prepare_messages(
            purpose, recipient, tone, length, include_subject
        )
        schema = EmailDraft if as_structured else None
        return self.engine.execute(messages=messages, output_schema=schema, **kwargs)

    async def arun(
        self,
        purpose: str,
        recipient: str = "Recipient",
        tone: str = "professional",
        length: str = "concise",
        include_subject: bool = True,
        as_structured: bool = False,
        **kwargs: Any,
    ) -> AgentResult[Any]:
        """Execute email draft generation asynchronously."""
        messages = self._prepare_messages(
            purpose, recipient, tone, length, include_subject
        )
        schema = EmailDraft if as_structured else None
        return await self.engine.aexecute(
            messages=messages, output_schema=schema, **kwargs
        )
