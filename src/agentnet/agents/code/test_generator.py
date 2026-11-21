"""TestGenerator agent implementation."""

from __future__ import annotations

from typing import Any

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import TEST_GENERATOR_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class TestGenerator(BaseAgent[str]):
    """Generates automated tests (unit tests, edge cases, error conditions)."""

    __test__ = False

    def __init__(
        self,
        model: str | None = None,
        default_language: str = "python",
        default_framework: str = "pytest",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_language = default_language
        self.default_framework = default_framework
        self._system_template = PromptTemplate(TEST_GENERATOR_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        code: str,
        language: str,
        framework: str,
        test_types: list[str] | None,
    ) -> list[ChatMessage]:
        if not code or not code.strip():
            raise ValidationError("TestGenerator requires non-empty code input.")

        types_desc = (
            ", ".join(test_types)
            if test_types
            else "unit tests, edge cases, input validation, and error paths"
        )
        system_content = self._system_template.format(
            language=language,
            framework=framework,
            test_types=types_desc,
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Code to generate tests for ({language}):\n<untrusted_user_input>\n{code}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        code: str,
        language: str | None = None,
        framework: str | None = None,
        test_types: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Generate test cases synchronously."""
        lang = language or self.default_language
        fw = framework or self.default_framework
        messages = self._prepare_messages(code, lang, fw, test_types)
        return self.engine.execute(messages=messages, **kwargs)

    async def arun(
        self,
        code: str,
        language: str | None = None,
        framework: str | None = None,
        test_types: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[str]:
        """Generate test cases asynchronously."""
        lang = language or self.default_language
        fw = framework or self.default_framework
        messages = self._prepare_messages(code, lang, fw, test_types)
        return await self.engine.aexecute(messages=messages, **kwargs)
