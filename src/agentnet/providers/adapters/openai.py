"""OpenAI model provider adapter."""

from __future__ import annotations

import json
from typing import Any

from agentnet.core.capabilities import ProviderCapabilities
from agentnet.core.requests import ModelRequest
from agentnet.core.responses import ModelResponse, ToolCall
from agentnet.core.results import UsageInfo
from agentnet.exceptions import (
    AuthenticationError,
    CapabilityError,
    ProviderError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    RateLimitError,
)
from agentnet.providers.base import ProviderAdapter


class OpenAIAdapter(ProviderAdapter):
    """Adapter for OpenAI models (GPT-4o, GPT-4.1, etc.)."""

    def __init__(
        self, api_key: str | None = None, base_url: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(api_key=api_key, **kwargs)
        self.base_url = base_url
        self._sync_client = None
        self._async_client = None

    def _get_sync_client(self) -> Any:
        if self._sync_client is None:
            try:
                import openai
            except ImportError as err:
                raise CapabilityError(
                    "OpenAI SDK is not installed. Install it with: pip install 'agentnet[openai]'"
                ) from err
            self._sync_client = openai.OpenAI(
                api_key=self.api_key, base_url=self.base_url
            )
        return self._sync_client

    def _get_async_client(self) -> Any:
        if self._async_client is None:
            try:
                import openai
            except ImportError as err:
                raise CapabilityError(
                    "OpenAI SDK is not installed. Install it with: pip install 'agentnet[openai]'"
                ) from err
            self._async_client = openai.AsyncOpenAI(
                api_key=self.api_key, base_url=self.base_url
            )
        return self._async_client

    def _format_messages(self, request: ModelRequest) -> list[dict[str, Any]]:
        messages = []
        for msg in request.messages:
            formatted: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.name:
                formatted["name"] = msg.name
            if msg.tool_call_id:
                formatted["tool_call_id"] = msg.tool_call_id
            messages.append(formatted)
        return messages

    def _format_payload(self, request: ModelRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": self._format_messages(request),
            "temperature": request.temperature,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.stop:
            payload["stop"] = request.stop

        if request.output_schema:
            # Enforce JSON mode
            payload["response_format"] = {"type": "json_object"}

        if request.tools:
            payload["tools"] = request.tools

        payload.update(request.extra_options)
        return payload

    def _translate_exception(self, err: Exception) -> Exception:
        err_msg = str(err)
        err_type = type(err).__name__
        if "AuthenticationError" in err_type:
            return AuthenticationError(
                f"OpenAI Authentication failed: {err_msg}", provider="openai"
            )
        if "RateLimitError" in err_type:
            return RateLimitError(
                f"OpenAI Rate limit exceeded: {err_msg}", provider="openai"
            )
        if "APITimeoutError" in err_type:
            return ProviderTimeoutError(
                f"OpenAI Request timed out: {err_msg}", provider="openai"
            )
        if "APIConnectionError" in err_type:
            return ProviderUnavailableError(
                f"OpenAI Service unavailable or unreachable: {err_msg}",
                provider="openai",
            )
        if "APIError" in err_type:
            return ProviderError(f"OpenAI Provider error: {err_msg}", provider="openai")
        return err

    def _parse_completion(self, completion: Any) -> ModelResponse:
        choice = completion.choices[0]
        message = choice.message
        content = message.content

        tool_calls: list[ToolCall] = []
        if getattr(message, "tool_calls", None):
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments or "{}"),
                    )
                )

        usage = UsageInfo()
        if getattr(completion, "usage", None):
            usage = UsageInfo(
                prompt_tokens=completion.usage.prompt_tokens,
                completion_tokens=completion.usage.completion_tokens,
                total_tokens=completion.usage.total_tokens,
            )

        return ModelResponse(
            content=content,
            tool_calls=tool_calls,
            usage=usage,
            model=completion.model,
            finish_reason=choice.finish_reason or "stop",
            raw=completion,
        )

    def generate(self, request: ModelRequest) -> ModelResponse:
        client = self._get_sync_client()
        payload = self._format_payload(request)
        try:
            completion = client.chat.completions.create(**payload)
            return self._parse_completion(completion)
        except Exception as err:
            raise self._translate_exception(err) from err

    async def agenerate(self, request: ModelRequest) -> ModelResponse:
        client = self._get_async_client()
        payload = self._format_payload(request)
        try:
            completion = await client.chat.completions.create(**payload)
            return self._parse_completion(completion)
        except Exception as err:
            raise self._translate_exception(err) from err

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_structured_output=True,
            supports_tools=True,
            supports_streaming=True,
            supports_async=True,
            supports_vision=True,
        )
