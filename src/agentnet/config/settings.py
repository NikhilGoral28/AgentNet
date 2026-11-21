"""AgentNet Configuration and Settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentConfig:
    """AgentNet configuration options."""

    provider: str | None = None
    model: str | None = None
    api_key: str | None = field(default=None, repr=False)
    temperature: float = 0.7
    max_tokens: int | None = None
    timeout: float = 60.0
    max_retries: int = 3
    log_content: bool = True
    output_schema: type | None = None
    extra_options: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        masked_key = "[REDACTED]" if self.api_key else None
        return (
            f"AgentConfig(provider={self.provider!r}, model={self.model!r}, "
            f"api_key={masked_key!r}, temperature={self.temperature}, "
            f"timeout={self.timeout}, max_retries={self.max_retries}, "
            f"log_content={self.log_content})"
        )

    @classmethod
    def from_env(cls, **overrides: Any) -> AgentConfig:
        """Create configuration resolved from environment variables and explicit overrides."""
        provider = overrides.get("provider") or os.environ.get(
            "AGENTNET_PROVIDER", "openai"
        )
        model = overrides.get("model") or os.environ.get("AGENTNET_MODEL", "gpt-4.1")

        # Parse model string like "openai/gpt-4.1" if provided
        if "/" in model and not overrides.get("provider"):
            parts = model.split("/", 1)
            provider = parts[0]
            model = parts[1]

        timeout_env = os.environ.get("AGENTNET_TIMEOUT")
        timeout = float(timeout_env) if timeout_env else overrides.get("timeout", 60.0)

        retries_env = os.environ.get("AGENTNET_MAX_RETRIES")
        max_retries = (
            int(retries_env) if retries_env else overrides.get("max_retries", 3)
        )

        log_content_env = os.environ.get("AGENTNET_LOG_CONTENT")
        log_content = (
            log_content_env.lower() not in ("0", "false", "no")
            if log_content_env is not None
            else overrides.get("log_content", True)
        )

        api_key = overrides.get("api_key")
        if not api_key:
            if provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
            elif provider in ("grok", "xai"):
                api_key = os.environ.get("XAI_API_KEY") or os.environ.get(
                    "GROK_API_KEY"
                )
            elif provider == "anthropic":
                api_key = os.environ.get("ANTHROPIC_API_KEY")
            elif provider in ("gemini", "google"):
                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
                    "GOOGLE_API_KEY"
                )

        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=overrides.get("temperature", 0.7),
            max_tokens=overrides.get("max_tokens"),
            timeout=timeout,
            max_retries=max_retries,
            log_content=log_content,
            output_schema=overrides.get("output_schema"),
            extra_options=overrides.get("extra_options", {}),
        )
