"""Model request representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    """A single normalized chat message."""

    role: str  # "system", "user", "assistant", "tool"
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass
class ModelRequest:
    """Normalized request dispatched to a ProviderAdapter."""

    messages: list[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None
    output_schema: type | None = None
    tools: list[dict[str, Any]] = field(default_factory=list)
    stop: list[str] | None = None
    extra_options: dict[str, Any] = field(default_factory=dict)
