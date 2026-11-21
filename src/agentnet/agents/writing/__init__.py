"""Writing and communication agents."""

from agentnet.agents.writing.email_responder import EmailResponder, EmailResponseDraft
from agentnet.agents.writing.email_writer import EmailDraft, EmailWriter
from agentnet.agents.writing.meeting_notes_writer import (
    ActionItem,
    MeetingNotes,
    MeetingNotesWriter,
)

__all__ = [
    "ActionItem",
    "EmailDraft",
    "EmailResponder",
    "EmailResponseDraft",
    "EmailWriter",
    "MeetingNotes",
    "MeetingNotesWriter",
]
