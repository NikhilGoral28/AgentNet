"""Model response representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentnet.core.results import UsageInfo


@dataclass
class ToolCall:
    """Represents a tool call requested by a model."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ModelResponse:
    """Normalized response returned from a ProviderAdapter."""

    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: UsageInfo = field(default_factory=UsageInfo)
    model: str = ""
    finish_reason: str = "stop"
    raw: Any = None
