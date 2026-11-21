"""CodeReviewer agent implementation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import CODE_REVIEWER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class CodeIssue(BaseModel):
    """An issue identified during code review."""

    severity: Literal["critical", "high", "medium", "low", "info"] = "medium"
    category: str = "general"
    line_number: int | None = None
    description: str
    recommendation: str


class CodeReviewResult(BaseModel):
    """Structured result returned by CodeReviewer."""

    summary: str
    overall_score: int = Field(default=85, ge=0, le=100)
    issues: list[CodeIssue] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class CodeReviewer(BaseAgent[CodeReviewResult]):
    """Reviews code for bugs, vulnerabilities, performance issues, and maintainability."""

    def __init__(
        self,
        model: str | None = None,
        default_language: str = "python",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_language = default_language
        self._system_template = PromptTemplate(CODE_REVIEWER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        code: str,
        language: str,
        focus_areas: list[str] | None,
    ) -> list[ChatMessage]:
        if not code or not code.strip():
            raise ValidationError("CodeReviewer requires non-empty code input.")

        focus_desc = (
            ", ".join(focus_areas)
            if focus_areas
            else "all aspects (correctness, security, performance, clean code)"
        )
        system_content = self._system_template.format(
            language=language,
            focus_areas=focus_desc,
        )

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Code to review ({language}):\n<untrusted_user_input>\n{code}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        code: str,
        language: str | None = None,
        focus_areas: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[CodeReviewResult]:
        """Execute code review synchronously."""
        lang = language or self.default_language
        messages = self._prepare_messages(code, lang, focus_areas)
        return self.engine.execute(
            messages=messages,
            output_schema=CodeReviewResult,
            **kwargs,
        )

    async def arun(
        self,
        code: str,
        language: str | None = None,
        focus_areas: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[CodeReviewResult]:
        """Execute code review asynchronously."""
        lang = language or self.default_language
        messages = self._prepare_messages(code, lang, focus_areas)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=CodeReviewResult,
            **kwargs,
        )
