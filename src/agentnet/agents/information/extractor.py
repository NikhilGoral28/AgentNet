"""Extractor agent implementation for structured data extraction."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import EXTRACTOR_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate

T = TypeVar("T", bound=BaseModel)


class Extractor(BaseAgent[T], Generic[T]):
    """Extracts structured fields and entities from text into a validated Pydantic schema."""

    def __init__(
        self,
        output_schema: type[T],
        model: str | None = None,
        instructions: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        if not issubclass(output_schema, BaseModel):
            raise ValidationError(
                "Extractor requires output_schema to be a subclass of pydantic.BaseModel."
            )
        self.output_schema = output_schema
        self.instructions = instructions or ""
        self._system_template = PromptTemplate(EXTRACTOR_SYSTEM_PROMPT)

    def _prepare_messages(self, text: str) -> list[ChatMessage]:
        if not text or not text.strip():
            raise ValidationError("Extractor requires non-empty text input.")

        schema_json = self.output_schema.model_json_schema()
        system_content = (
            f"{self._system_template.template}\n\n"
            f"Target Schema ({self.output_schema.__name__}):\n{schema_json}\n"
        )
        if self.instructions:
            system_content += f"\nAdditional Instructions:\n{self.instructions}\n"

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Text to extract from:\n<untrusted_user_input>\n{text}\n</untrusted_user_input>",
            ),
        ]

    def run(self, text: str, **kwargs: Any) -> AgentResult[T]:
        """Execute extraction synchronously."""
        messages = self._prepare_messages(text)
        return self.engine.execute(
            messages=messages,
            output_schema=self.output_schema,
            **kwargs,
        )

    async def arun(self, text: str, **kwargs: Any) -> AgentResult[T]:
        """Execute extraction asynchronously."""
        messages = self._prepare_messages(text)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=self.output_schema,
            **kwargs,
        )
