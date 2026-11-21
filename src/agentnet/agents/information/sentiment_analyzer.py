"""SentimentAnalyzer agent implementation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import SENTIMENT_ANALYZER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class SentimentResult(BaseModel):
    """Structured result returned by SentimentAnalyzer."""

    sentiment: Literal["positive", "negative", "neutral", "mixed"] = "neutral"
    polarity: float = Field(default=0.0, ge=-1.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    key_aspects: list[str] = Field(default_factory=list)
    reasoning: str | None = None


class SentimentAnalyzer(BaseAgent[SentimentResult]):
    """Estimates sentiment, polarity (-1.0 to 1.0), confidence, and key emotional aspects."""

    def __init__(
        self,
        model: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self._system_template = PromptTemplate(SENTIMENT_ANALYZER_SYSTEM_PROMPT)

    def _prepare_messages(self, text: str) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("SentimentAnalyzer requires non-empty text input.")

        system_content = self._system_template.format()

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Text to analyze for sentiment:\n<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(self, text: str, **kwargs: Any) -> AgentResult[SentimentResult]:
        """Execute sentiment analysis synchronously."""
        messages = self._prepare_messages(text)
        return self.engine.execute(
            messages=messages,
            output_schema=SentimentResult,
            **kwargs,
        )

    async def arun(self, text: str, **kwargs: Any) -> AgentResult[SentimentResult]:
        """Execute sentiment analysis asynchronously."""
        messages = self._prepare_messages(text)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=SentimentResult,
            **kwargs,
        )
