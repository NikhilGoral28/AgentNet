"""Classifier agent implementation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import OutputParsingError, ValidationError
from agentnet.prompts.defaults import CLASSIFIER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class ClassificationResult(BaseModel):
    """Result returned by Classifier agent."""

    category: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: str | None = None


class Classifier(BaseAgent[ClassificationResult]):
    """Classifies text into predefined categories with confidence estimation."""

    def __init__(
        self,
        categories: list[str],
        model: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        if not categories:
            raise ValidationError("Classifier requires a non-empty list of categories.")
        self.categories = categories
        self._system_template = PromptTemplate(CLASSIFIER_SYSTEM_PROMPT)

    def _prepare_messages(self, text: str) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("Classifier requires non-empty text input.")

        formatted_categories = "\n".join(f"- {c}" for c in self.categories)
        system_content = self._system_template.format(categories=formatted_categories)

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Text to classify:\n<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(self, text: str, **kwargs: Any) -> AgentResult[ClassificationResult]:
        """Execute classification synchronously."""
        messages = self._prepare_messages(text)
        result = self.engine.execute(
            messages=messages,
            output_schema=ClassificationResult,
            **kwargs,
        )

        # Enforce that category is in allowed categories
        if result.output.category not in self.categories:
            # Case-insensitive match check
            matched = next(
                (
                    c
                    for c in self.categories
                    if c.lower() == result.output.category.lower()
                ),
                None,
            )
            if matched:
                result.output.category = matched
            else:
                raise OutputParsingError(
                    f"Model selected '{result.output.category}' which is not in permitted categories: {self.categories}",
                    schema=ClassificationResult,
                )

        return result

    async def arun(self, text: str, **kwargs: Any) -> AgentResult[ClassificationResult]:
        """Execute classification asynchronously."""
        messages = self._prepare_messages(text)
        result = await self.engine.aexecute(
            messages=messages,
            output_schema=ClassificationResult,
            **kwargs,
        )

        if result.output.category not in self.categories:
            matched = next(
                (
                    c
                    for c in self.categories
                    if c.lower() == result.output.category.lower()
                ),
                None,
            )
            if matched:
                result.output.category = matched
            else:
                raise OutputParsingError(
                    f"Model selected '{result.output.category}' which is not in permitted categories: {self.categories}",
                    schema=ClassificationResult,
                )

        return result
