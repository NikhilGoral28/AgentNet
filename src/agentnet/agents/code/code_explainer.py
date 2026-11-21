"""CodeExplainer agent implementation."""

from __future__ import annotations

from typing import Any

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import CODE_EXPLAINER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class CodeExplainer(BaseAgent[str]):
    """Explains code architecture, logic flow, algorithms, and complexity."""

    def __init__(
        self,
        model: str | None = None,
        default_language: str = "python",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_language = default_language
        self._system_template = PromptTemplate(CODE_EXPLAINER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        code: str,
        language: str,
        audience: str,
        include_complexity: bool,
    ) -> list[ChatMessage]:
        if not code or not code.strip():
            raise ValidationError("CodeExplainer requires non-empty code input.")

        system_content = self._system_template.format(
            language=language,
            audience=audience,
            include_complexity="Yes" if include_complexity else "No",
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Code to explain ({language}):\n<untrusted_user_input>\n{code}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        code: str,
        language: str | None = None,
        audience: str = "developer",
        include_complexity: bool = True,
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute code explanation synchronously."""
        lang = language or self.default_language
        messages = self._prepare_messages(code, lang, audience, include_complexity)
        return self.engine.execute(messages=messages, **kwargs)

    async def arun(
        self,
        code: str,
        language: str | None = None,
        audience: str = "developer",
        include_complexity: bool = True,
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Execute code explanation asynchronously."""
        lang = language or self.default_language
        messages = self._prepare_messages(code, lang, audience, include_complexity)
        return await self.engine.aexecute(messages=messages, **kwargs)
