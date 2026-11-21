"""Proofreader agent implementation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import PROOFREADER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class CorrectionItem(BaseModel):
    """An individual correction made by Proofreader."""

    original: str
    replacement: str
    category: Literal["grammar", "spelling", "punctuation", "style", "clarity"] = (
        "grammar"
    )
    explanation: str


class ProofreadResult(BaseModel):
    """Structured result returned by Proofreader."""

    corrected_text: str
    corrections_count: int = 0
    corrections: list[CorrectionItem] = Field(default_factory=list)
    summary: str | None = None


class Proofreader(BaseAgent[ProofreadResult]):
    """Corrects grammar, spelling, punctuation, and style with itemized change tracking."""

    def __init__(
        self,
        model: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self._system_template = PromptTemplate(PROOFREADER_SYSTEM_PROMPT)

    def _prepare_messages(self, text: str) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("Proofreader requires non-empty text input.")

        system_content = self._system_template.format()

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Text to proofread:\n<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(self, text: str, **kwargs: Any) -> AgentResult[ProofreadResult]:
        """Execute proofreading synchronously."""
        messages = self._prepare_messages(text)
        result = self.engine.execute(
            messages=messages,
            output_schema=ProofreadResult,
            **kwargs,
        )
        if not result.output.corrections_count and result.output.corrections:
            result.output.corrections_count = len(result.output.corrections)
        return result

    async def arun(self, text: str, **kwargs: Any) -> AgentResult[ProofreadResult]:
        """Execute proofreading asynchronously."""
        messages = self._prepare_messages(text)
        result = await self.engine.aexecute(
            messages=messages,
            output_schema=ProofreadResult,
            **kwargs,
        )
        if not result.output.corrections_count and result.output.corrections:
            result.output.corrections_count = len(result.output.corrections)
        return result
