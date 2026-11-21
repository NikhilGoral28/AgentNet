"""Provider capabilities definition."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderCapabilities:
    """Declares capabilities supported by a model provider adapter."""

    supports_structured_output: bool = True
    supports_tools: bool = True
    supports_streaming: bool = False
    supports_async: bool = True
    supports_vision: bool = False
    max_context_tokens: int | None = None
