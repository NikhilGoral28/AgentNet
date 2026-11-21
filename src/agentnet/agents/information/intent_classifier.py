"""IntentClassifier agent implementation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import INTENT_CLASSIFIER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class IntentResult(BaseModel):
    """Structured result returned by IntentClassifier."""

    intent: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    entities: dict[str, Any] = Field(default_factory=dict)
    reasoning: str | None = None


class IntentClassifier(BaseAgent[IntentResult]):
    """Classifies user intent and extracts relevant semantic parameters/entities."""

    def __init__(
        self,
        candidate_intents: list[str] | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.candidate_intents = candidate_intents or []
        self._system_template = PromptTemplate(INTENT_CLASSIFIER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        text: str,
        intents: list[str] | None,
    ) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("IntentClassifier requires non-empty text input.")

        active_intents = intents if intents is not None else self.candidate_intents
        intents_desc = (
            ", ".join(active_intents)
            if active_intents
            else "Open domain / Infer most appropriate intent"
        )

        system_content = self._system_template.format(candidate_intents=intents_desc)

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"User input to classify intent:\n<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        text: str,
        candidate_intents: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[IntentResult]:
        """Execute intent classification synchronously."""
        messages = self._prepare_messages(text, candidate_intents)
        return self.engine.execute(
            messages=messages,
            output_schema=IntentResult,
            **kwargs,
        )

    async def arun(
        self,
        text: str,
        candidate_intents: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[IntentResult]:
        """Execute intent classification asynchronously."""
        messages = self._prepare_messages(text, candidate_intents)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=IntentResult,
            **kwargs,
        )
