"""Rewriter agent implementation."""

from __future__ import annotations

from typing import Any

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import REWRITER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class Rewriter(BaseAgent[str]):
    """Rewrites content for tone, audience, clarity, formality, or length constraints."""

    def __init__(
        self,
        model: str | None = None,
        default_tone: str = "professional",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_tone = default_tone
        self._system_template = PromptTemplate(REWRITER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        text: str,
        tone: str,
        audience: str,
        length_constraint: str | None,
    ) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("Rewriter requires non-empty text input.")

        length_desc = length_constraint or "Preserve approximate original length."
        system_content = self._system_template.format(
            tone=tone,
            audience=audience,
            length_constraint=length_desc,
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Text to rewrite:\n<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        text: str,
        tone: str | None = None,
        audience: str = "general",
        length_constraint: str | None = None,
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute text rewriting synchronously."""
        chosen_tone = tone or self.default_tone
        messages = self._prepare_messages(
            text, chosen_tone, audience, length_constraint
        )
        return self.engine.execute(messages=messages, **kwargs)

    async def arun(
        self,
        text: str,
        tone: str | None = None,
        audience: str = "general",
        length_constraint: str | None = None,
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute text rewriting asynchronously."""
        chosen_tone = tone or self.default_tone
        messages = self._prepare_messages(
            text, chosen_tone, audience, length_constraint
        )
        return await self.engine.aexecute(messages=messages, **kwargs)
