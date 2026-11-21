"""Summarizer agent implementation."""

from __future__ import annotations

from typing import Any

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import SUMMARIZER_SYSTEM_PROMPT, SUMMARIZER_USER_PROMPT
from agentnet.prompts.templates import PromptTemplate


class Summarizer(BaseAgent[str]):
    """Condenses text into summaries with configurable style, length, and audience."""

    def __init__(
        self,
        model: str | None = None,
        default_style: str = "bullet_points",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_style = default_style
        self._system_template = PromptTemplate(SUMMARIZER_SYSTEM_PROMPT)
        self._user_template = PromptTemplate(SUMMARIZER_USER_PROMPT)

    def _prepare_messages(
        self,
        text: str,
        style: str,
        max_words: int | None,
        audience: str,
    ) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("Summarizer requires non-empty text input.")

        length_desc = (
            f"Maximum {max_words} words." if max_words else "Concise and comprehensive."
        )
        system_content = self._system_template.format(
            style=style,
            max_words_instruction=length_desc,
            audience=audience,
        )
        user_content = self._user_template.format(text=text)

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(role="user", content=user_content),
        ]

    def run(
        self,
        text: str,
        style: str | None = None,
        max_words: int | None = None,
        audience: str = "general",
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute summarization synchronously."""
        chosen_style = style or self.default_style
        messages = self._prepare_messages(text, chosen_style, max_words, audience)
        return self.engine.execute(messages=messages, **kwargs)

    async def arun(
        self,
        text: str,
        style: str | None = None,
        max_words: int | None = None,
        audience: str = "general",
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute summarization asynchronously."""
        chosen_style = style or self.default_style
        messages = self._prepare_messages(text, chosen_style, max_words, audience)
        return await self.engine.aexecute(messages=messages, **kwargs)
