"""Translator agent implementation."""

from __future__ import annotations

from typing import Any

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import TRANSLATOR_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class Translator(BaseAgent[str]):
    """Translates text between languages while preserving meaning and tone."""

    def __init__(
        self,
        model: str | None = None,
        default_target_language: str = "English",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_target_language = default_target_language
        self._system_template = PromptTemplate(TRANSLATOR_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        text: str,
        target_language: str,
        source_language: str,
    ) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("Translator requires non-empty text input.")

        system_content = self._system_template.format(
            source_language=source_language,
            target_language=target_language,
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        text: str,
        target_language: str | None = None,
        source_language: str = "auto-detected language",
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute translation synchronously."""
        target = target_language or self.default_target_language
        messages = self._prepare_messages(text, target, source_language)
        return self.engine.execute(messages=messages, **kwargs)

    async def arun(
        self,
        text: str,
        target_language: str | None = None,
        source_language: str = "auto-detected language",
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute translation asynchronously."""
        target = target_language or self.default_target_language
        messages = self._prepare_messages(text, target, source_language)
        return await self.engine.aexecute(messages=messages, **kwargs)
