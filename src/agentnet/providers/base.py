"""Base Provider Adapter definition."""

from __future__ import annotations

from abc import ABC, abstractmethod

from agentnet.core.capabilities import ProviderCapabilities
from agentnet.core.requests import ModelRequest
from agentnet.core.responses import ModelResponse


class ProviderAdapter(ABC):
    """Abstract base class for model provider adapters."""

    def __init__(self, api_key: str | None = None, **kwargs: object) -> None:
        self.api_key = api_key
        self.options = kwargs

    @abstractmethod
    def generate(self, request: ModelRequest) -> ModelResponse:
        """Synchronously execute a model request and return a normalized response."""
        ...

    @abstractmethod
    async def agenerate(self, request: ModelRequest) -> ModelResponse:
        """Asynchronously execute a model request and return a normalized response."""
        ...

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Return declared capabilities supported by this provider."""
        ...
