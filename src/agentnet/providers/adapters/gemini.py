"""Google Gemini model provider adapter."""

from __future__ import annotations

import os
from typing import Any

from agentnet.core.capabilities import ProviderCapabilities
from agentnet.exceptions import (
    AuthenticationError,
    CapabilityError,
    ProviderError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)
from agentnet.providers.adapters.openai import OpenAIAdapter

DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class GeminiAdapter(OpenAIAdapter):
    """Adapter for Google Gemini models (gemini-2.5-flash, gemini-2.5-pro, gemini-1.5-flash, gemini-1.5-pro, etc.).

    Communicates with Google Gemini's OpenAI-compatible API endpoint at
    https://generativelanguage.googleapis.com/v1beta/openai/.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        resolved_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        resolved_base_url = (
            base_url or os.environ.get("GEMINI_BASE_URL") or DEFAULT_GEMINI_BASE_URL
        )
        super().__init__(api_key=resolved_key, base_url=resolved_base_url, **kwargs)

    def _get_sync_client(self) -> Any:
        try:
            import openai
        except ImportError as err:
            raise CapabilityError(
                "OpenAI SDK is required to connect to Gemini OpenAI-compatible endpoint. "
                "Install with: pip install 'agentnet[openai]'"
            ) from err
        if self._sync_client is None:
            self._sync_client = openai.OpenAI(
                api_key=self.api_key, base_url=self.base_url
            )
        return self._sync_client

    def _get_async_client(self) -> Any:
        try:
            import openai
        except ImportError as err:
            raise CapabilityError(
                "OpenAI SDK is required to connect to Gemini OpenAI-compatible endpoint. "
                "Install with: pip install 'agentnet[openai]'"
            ) from err
        if self._async_client is None:
            self._async_client = openai.AsyncOpenAI(
                api_key=self.api_key, base_url=self.base_url
            )
        return self._async_client

    def _translate_exception(self, err: Exception) -> Exception:
        err_msg = str(err)
        err_type = type(err).__name__
        if "AuthenticationError" in err_type:
            return AuthenticationError(
                f"Gemini Authentication failed: {err_msg}", provider="gemini"
            )
        if "RateLimitError" in err_type:
            return RateLimitError(
                f"Gemini Rate limit exceeded: {err_msg}", provider="gemini"
            )
        if "APITimeoutError" in err_type:
            return ProviderTimeoutError(
                f"Gemini Request timed out: {err_msg}", provider="gemini"
            )
        if "APIConnectionError" in err_type:
            return ProviderUnavailableError(
                f"Gemini Service unavailable or unreachable: {err_msg}",
                provider="gemini",
            )
        if "APIError" in err_type:
            return ProviderError(f"Gemini Provider error: {err_msg}", provider="gemini")
        return err

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_structured_output=True,
            supports_tools=True,
            supports_streaming=True,
            supports_async=True,
            supports_vision=True,
        )
