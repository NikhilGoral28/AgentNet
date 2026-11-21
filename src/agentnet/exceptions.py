"""AgentNet Exception Hierarchy.

All library exceptions inherit from AgentNetError. Sensitive values (API keys,
tokens) are redacted from string representations to prevent accidental leakage
into logs or external monitors.
"""

from __future__ import annotations

import re
from typing import Any

_SECRET_PATTERNS = [
    re.compile(r"sk-(?:proj-|ant-)?[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
    re.compile(r"xai-[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
    re.compile(r"AIzaSy[a-zA-Z0-9_\-]{30,45}", re.IGNORECASE),
    re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
    re.compile(
        r"(?:api[-_]?key|auth[-_]?token|secret|password)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-\.]{12,}['\"]?",
        re.IGNORECASE,
    ),
    re.compile(
        r"eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]{10,}",
        re.IGNORECASE,
    ),
    re.compile(
        r"-----BEGIN[ A-Z0-9_-]+PRIVATE KEY-----[\s\S]*?-----END[ A-Z0-9_-]+PRIVATE KEY-----"
    ),
]


def _sanitize(message: str) -> str:
    """Redact potential API keys, private keys, or tokens from error messages."""
    result = str(message)
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED_SECRET]", result)
    return result


def _sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively sanitize dictionary values and sensitive keys."""
    sanitized: dict[str, Any] = {}
    sensitive_keys = {"api_key", "token", "password", "secret", "authorization"}
    for k, v in data.items():
        if any(s in k.lower() for s in sensitive_keys):
            sanitized[k] = "[REDACTED_SECRET]"
        elif isinstance(v, str):
            sanitized[k] = _sanitize(v)
        elif isinstance(v, dict):
            sanitized[k] = _sanitize_dict(v)
        else:
            sanitized[k] = v
    return sanitized


class AgentNetError(Exception):
    """Base exception for all AgentNet errors."""

    def __init__(
        self, message: str, *args: Any, details: dict[str, Any] | None = None
    ) -> None:
        sanitized_msg = _sanitize(message)
        super().__init__(sanitized_msg, *args)
        self.raw_message = sanitized_msg
        self.details = _sanitize_dict(details) if details else {}

    def __str__(self) -> str:
        return self.raw_message


class ConfigurationError(AgentNetError):
    """Raised when configuration is invalid, incomplete, or missing."""


class ValidationError(AgentNetError):
    """Raised when task inputs fail validation before provider execution."""


class ProviderError(AgentNetError):
    """Raised when an external model provider fails or returns an error."""

    def __init__(
        self,
        message: str,
        *args: Any,
        provider: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, *args, details=details)
        self.provider = provider
        self.status_code = status_code


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails (e.g., invalid API key)."""


class RateLimitError(ProviderError):
    """Raised when the provider rate limit or quota is exceeded."""


class ProviderTimeoutError(ProviderError):
    """Raised when a request to a provider times out."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider service is unreachable or returning 5xx errors."""


class OutputParsingError(AgentNetError):
    """Raised when model output cannot be parsed or validated against the schema."""

    def __init__(
        self,
        message: str,
        *args: Any,
        raw_output: str | None = None,
        schema: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, *args, details=details)
        self.raw_output = raw_output
        self.schema = schema


class CapabilityError(AgentNetError):
    """Raised when requesting a feature not supported by the selected provider or model."""


class ToolError(AgentNetError):
    """Raised when a tool fails during execution."""

    def __init__(
        self,
        message: str,
        *args: Any,
        tool_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, *args, details=details)
        self.tool_name = tool_name


class ToolPermissionError(ToolError):
    """Raised when a tool invocation violates configured permissions or approval policies."""


class ToolTimeoutError(ToolError):
    """Raised when tool execution exceeds the configured timeout."""


class WorkflowError(AgentNetError):
    """Raised when a workflow fails during execution."""

    def __init__(
        self,
        message: str,
        *args: Any,
        step_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, *args, details=details)
        self.step_id = step_id


class WorkflowLimitError(WorkflowError):
    """Raised when workflow iteration, duration, or recursion limits are exceeded."""


class WorkflowStepError(WorkflowError):
    """Raised when an individual workflow step fails."""


class ExecutionCancelledError(AgentNetError):
    """Raised when an agent or workflow execution is cancelled."""
