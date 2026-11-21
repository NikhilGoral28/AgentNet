"""MeetingNotesWriter agent implementation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agentnet.core.base import BaseAgent
from agentnet.core.requests import ChatMessage
from agentnet.core.results import AgentResult
from agentnet.exceptions import ValidationError
from agentnet.prompts.defaults import MEETING_NOTES_SYSTEM_PROMPT
from agentnet.prompts.templates import PromptTemplate


class ActionItem(BaseModel):
    """An action item assigned during a meeting."""

    task: str
    assignee: str | None = None
    due_date: str | None = None


class MeetingNotes(BaseModel):
    """Structured meeting notes containing summary, decisions, and action items."""

    title: str = "Meeting Notes"
    summary: str
    attendees: list[str] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)


class MeetingNotesWriter(BaseAgent[MeetingNotes]):
    """Transforms raw meeting transcripts or discussion notes into structured action items and decisions."""

    def __init__(
        self,
        model: str | None = None,
        default_title: str = "Meeting Notes",
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, **kwargs)
        self.default_title = default_title
        self._system_template = PromptTemplate(MEETING_NOTES_SYSTEM_PROMPT)

    def _prepare_messages(
        self,
        transcript: str,
        meeting_title: str | None,
    ) -> list[ChatMessage]:
        if not transcript or not transcript.strip():
            raise ValidationError(
                "MeetingNotesWriter requires non-empty transcript input."
            )

        title = meeting_title or self.default_title
        system_content = self._system_template.format(meeting_title=title)

        return [
            ChatMessage(role="system", content=system_content),
            ChatMessage(
                role="user",
                content=f"Meeting Transcript / Discussion points:\n<untrusted_user_input>\n{transcript}\n</untrusted_user_input>",
            ),
        ]

    def run(
        self,
        transcript: str,
        meeting_title: str | None = None,
        **kwargs: Any,
    ) -> AgentResult[MeetingNotes]:
        """Generate meeting notes synchronously."""
        messages = self._prepare_messages(transcript, meeting_title)
        return self.engine.execute(
            messages=messages,
            output_schema=MeetingNotes,
            **kwargs,
        )

    async def arun(
        self,
        transcript: str,
        meeting_title: str | None = None,
        **kwargs: Any,
    ) -> AgentResult[MeetingNotes]:
        """Generate meeting notes asynchronously."""
        messages = self._prepare_messages(transcript, meeting_title)
        return await self.engine.aexecute(
            messages=messages,
            output_schema=MeetingNotes,
            **kwargs,
        )
