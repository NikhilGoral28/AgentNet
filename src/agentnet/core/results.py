"""Result models for AgentNet."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class UsageInfo:
    """Normalized token and resource usage information."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float | None = None
    currency: str = "USD"


@dataclass(frozen=True)
class AgentResult(Generic[T]):
    """Standardized result returned by all AgentNet agents and workflows."""

    output: T
    run_id: str
    model: str
    duration: float
    usage: UsageInfo = field(default_factory=UsageInfo)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"AgentResult(output={self.output!r}, model={self.model!r}, "
            f"duration={self.duration:.2f}s, run_id={self.run_id!r})"
        )
