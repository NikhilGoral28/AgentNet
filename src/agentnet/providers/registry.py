"""Provider registry and factory."""

from __future__ import annotations

from typing import Any

from agentnet.exceptions import ConfigurationError
from agentnet.providers.adapters.fake import FakeProviderAdapter
from agentnet.providers.adapters.gemini import GeminiAdapter
from agentnet.providers.adapters.grok import GrokAdapter
from agentnet.providers.adapters.openai import OpenAIAdapter
from agentnet.providers.base import ProviderAdapter

_PROVIDER_REGISTRY: dict[str, type[ProviderAdapter]] = {
    "openai": OpenAIAdapter,
    "grok": GrokAdapter,
    "xai": GrokAdapter,
    "gemini": GeminiAdapter,
    "google": GeminiAdapter,
    "fake": FakeProviderAdapter,
    "mock": FakeProviderAdapter,
}


def register_provider(name: str, adapter_cls: type[ProviderAdapter]) -> None:
    """Register a custom provider adapter class."""
    _PROVIDER_REGISTRY[name.lower()] = adapter_cls


def get_provider(name: str, **kwargs: Any) -> ProviderAdapter:
    """Instantiate a provider adapter by name."""
    provider_key = name.lower()
    adapter_cls = _PROVIDER_REGISTRY.get(provider_key)
    if not adapter_cls:
        available = ", ".join(_PROVIDER_REGISTRY.keys())
        raise ConfigurationError(
            f"Unknown provider '{name}'. Available registered providers: {available}"
        )
    return adapter_cls(**kwargs)
