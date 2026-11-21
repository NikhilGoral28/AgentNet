"""Fake provider adapter for offline tests and deterministic verification."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel

from agentnet.core.capabilities import ProviderCapabilities
from agentnet.core.requests import ModelRequest
from agentnet.core.responses import ModelResponse
from agentnet.core.results import UsageInfo
from agentnet.providers.base import ProviderAdapter


class FakeProviderAdapter(ProviderAdapter):
    """Test provider adapter that returns programmed responses without network calls."""

    def __init__(
        self,
        default_response: str | None = None,
        response_fn: Callable[[ModelRequest], str | dict[str, Any]] | None = None,
        exception_to_raise: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.default_response = default_response
        self.response_fn = response_fn
        self.exception_to_raise = exception_to_raise
        self.call_count = 0
        self.last_request: ModelRequest | None = None

    def _build_response(self, request: ModelRequest) -> ModelResponse:
        self.call_count += 1
        self.last_request = request

        if self.exception_to_raise:
            raise self.exception_to_raise

        if self.response_fn:
            result = self.response_fn(request)
            if isinstance(result, dict):
                content = json.dumps(result)
            else:
                content = str(result)
        elif self.default_response is not None:
            content = self.default_response
        elif request.output_schema and issubclass(request.output_schema, BaseModel):
            # Generate minimal valid JSON for the schema if no specific response is set
            schema_fields = request.output_schema.model_fields
            dummy_data: dict[str, Any] = {}
            for field_name, field_info in schema_fields.items():
                annotation = field_info.annotation
                if annotation is str or annotation == (str | None):
                    dummy_data[field_name] = f"Sample {field_name}"
                elif annotation is int or annotation == (int | None):
                    dummy_data[field_name] = 42
                elif annotation is float or annotation == (float | None):
                    dummy_data[field_name] = 3.14
                elif annotation is bool or annotation == (bool | None):
                    dummy_data[field_name] = True
                else:
                    dummy_data[field_name] = None
            content = json.dumps(dummy_data)
        else:
            content = "This is a simulated model response."

        # Estimate fake token counts
        input_len = sum(len(m.content) for m in request.messages)
        prompt_tokens = max(1, input_len // 4)
        completion_tokens = max(1, len(content) // 4)

        return ModelResponse(
            content=content,
            model=request.model,
            usage=UsageInfo(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

    def generate(self, request: ModelRequest) -> ModelResponse:
        return self._build_response(request)

    async def agenerate(self, request: ModelRequest) -> ModelResponse:
        return self._build_response(request)

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_structured_output=True,
            supports_tools=True,
            supports_streaming=True,
            supports_async=True,
        )
