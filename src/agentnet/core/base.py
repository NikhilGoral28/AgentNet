"""BaseAgent definition for AgentNet."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from agentnet.config.settings import AgentConfig
from agentnet.core.engine import AgentEngine
from agentnet.core.results import AgentResult
from agentnet.providers.base import ProviderAdapter

T = TypeVar("T")


class BaseAgent(ABC, Generic[T]):
    """Abstract base class for all AgentNet agents."""

    def __init__(
        self,
        model: str | None = None,
        config: AgentConfig | None = None,
        provider_adapter: ProviderAdapter | None = None,
        **kwargs: Any,
    ) -> None:
        if config is not None:
            self.config = config
        else:
            self.config = AgentConfig.from_env(model=model, **kwargs)

        if model is not None:
            if "/" in model:
                parts = model.split("/", 1)
                self.config.provider = parts[0]
                self.config.model = parts[1]
            else:
                self.config.model = model

        self.engine: AgentEngine[T] = AgentEngine(
            config=self.config,
            provider_adapter=provider_adapter,
        )

    @abstractmethod
    def run(self, **kwargs: Any) -> AgentResult[T]:
        """Execute the agent synchronously."""
        ...

    async def arun(self, **kwargs: Any) -> AgentResult[T]:
        """Execute the agent asynchronously."""
        # Default async implementation falls back to synchronous execution if not overridden
        return self.run(**kwargs)
