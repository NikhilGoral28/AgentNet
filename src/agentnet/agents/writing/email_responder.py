"""EmailResponder agent implementation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import EMAIL_RESPONDER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class EmailResponseDraft(BaseModel):
    """Structured email reply draft."""

    subject: str
    body: str
    tone: str = "professional"


class EmailResponder(BaseAgent[EmailResponseDraft]):
    """Drafts contextual email replies using an existing conversation thread and explicit goal."""

    def __init__(
        self,
        model: str | None = None,
        default_tone: str = "professional",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_tone = default_tone
        self._system_template = PromptTemplate(EMAIL_RESPONDER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        thread: str,
        goal: str,
        tone: str,
        sender_name: str | None,
    ) -> list[ChatMessage]:
        if not thread or not thread.strip():
            raise ValidationError(
                "EmailResponder requires non-empty email thread input."
            )
        if not goal or not goal.strip():
            raise ValidationError("EmailResponder requires a clear response goal.")

        sender = sender_name or "Colleague / Client"
        system_content = self._system_template.format(
            sender_name=sender,
            goal=goal,
            tone=tone,
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=(
                    f"Email thread to reply to:\n<untrusted_user_input>\n{thread}\n</untrusted_user_input>\n\n"
                    f"Response Objective: {goal}"
                ),
            ),
        ]

    def run(
        self,
        thread: str,
        goal: str,
        tone: str | None = None,
        sender_name: str | None = None,
        **kwargs: Any,
    ) -> AgentResult[EmailResponseDraft]:
        """Draft email reply synchronously."""
        chosen_tone = tone or self.default_tone
        messages = self._prepare_messages(thread, goal, chosen_tone, sender_name)
        return self.engine.execute(
            messages=messages,
            output_schema=EmailResponseDraft,
            **kwargs,
        )

    async def arun(
        self,
        thread: str,
        goal: str,
        tone: str | None = None,
        sender_name: str | None = None,
        **kwargs: Any,
    ) -> AgentResult[EmailResponseDraft]:
        """Draft email reply asynchronously."""
        chosen_tone = tone or self.default_tone
        messages = self._prepare_messages(thread, goal, chosen_tone, sender_name)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=EmailResponseDraft,
            **kwargs,
        )
