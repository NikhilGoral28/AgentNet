"""TaskPlanner agent implementation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import TASK_PLANNER_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class PlanTask(BaseModel):
    """An individual actionable task in a plan."""

    id: int
    title: str
    description: str
    dependencies: list[int] = Field(default_factory=list)
    estimated_effort: str = "medium"
    exit_criteria: str | None = None


class PlanResult(BaseModel):
    """Structured plan returned by TaskPlanner."""

    goal: str
    summary: str
    tasks: list[PlanTask] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class TaskPlanner(BaseAgent[PlanResult]):
    """Deconstructs high-level goals into ordered, actionable task sequences with dependencies."""

    def __init__(
        self,
        model: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self._system_template = PromptTemplate(TASK_PLANNER_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        goal: str,
        constraints: list[str] | None,
    ) -> list[ChatMessage]:
        if not goal or not goal.strip():
            raise ValidationError("TaskPlanner requires a non-empty goal description.")

        constraints_desc = ", ".join(constraints) if constraints else "None specified"
        system_content = self._system_template.format(constraints=constraints_desc)

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Goal to plan:\n<untrusted_user_input>\n{goal}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        goal: str,
        constraints: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[PlanResult]:
        """Generate structured plan synchronously."""
        messages = self._prepare_messages(goal, constraints)
        return self.engine.execute(
            messages=messages,
            output_schema=PlanResult,
            **kwargs,
        )

    async def arun(
        self,
        goal: str,
        constraints: list[str] | None = None,
        **kwargs: Any,
    ) -> AgentResult[PlanResult]:
        """Generate structured plan asynchronously."""
        messages = self._prepare_messages(goal, constraints)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=PlanResult,
            **kwargs,
        )
