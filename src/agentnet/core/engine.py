import asyncio
import concurrent.futures
import json
import logging
import time
import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from agentnet.config.settings import AgentConfig
from agentnet.core.requests import ChatMessage, ModelRequest
from agentnet.core.results import AgentResult, UsageInfo
from agentnet.exceptions import (
    OutputParsingError,
    ProviderTimeoutError,
    RateLimitError,
    WorkflowLimitError,
)
from agentnet.providers.base import ProviderAdapter
from agentnet.providers.registry import get_provider
from agentnet.tools.base import Tool

logger = logging.getLogger("agentnet")

T = TypeVar("T")


def _extract_json_content(content: str) -> str:
    """Safely extract JSON substring without vulnerable backtracking regex."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            end_marker = cleaned.rfind("```")
            if end_marker > first_newline:
                cleaned = cleaned[first_newline + 1 : end_marker].strip()
    elif "{" in cleaned and "}" in cleaned:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            cleaned = cleaned[start : end + 1]
    return cleaned


class AgentEngine(Generic[T]):
    """Shared execution engine coordinating requests, providers, validation, and tools."""

    def __init__(
        self,
        config: AgentConfig | None = None,
        provider_adapter: ProviderAdapter | None = None,
    ) -> None:
        self.config = config or AgentConfig.from_env()
        self._custom_adapter = provider_adapter

    def resolve_adapter(self, config: AgentConfig) -> ProviderAdapter:
        """Resolve the provider adapter to use."""
        if self._custom_adapter:
            return self._custom_adapter
        provider_name = config.provider or "openai"
        return get_provider(
            provider_name,
            api_key=config.api_key,
            **config.extra_options,
        )

    def _parse_structured_output(
        self, content: str | None, schema: type[BaseModel]
    ) -> Any:
        """Parse and validate JSON content against a Pydantic schema."""
        if not content:
            raise OutputParsingError(
                "Model returned empty content when structured output was expected.",
                schema=schema,
            )

        cleaned = _extract_json_content(content)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise OutputParsingError(
                f"Failed to decode model output as JSON: {err}",
                raw_output=content,
                schema=schema,
            ) from err

        try:
            return schema.model_validate(data)
        except Exception as err:
            raise OutputParsingError(
                f"Model output failed validation against schema {schema.__name__}: {err}",
                raw_output=content,
                schema=schema,
            ) from err

    def execute(
        self,
        messages: list[ChatMessage],
        config: AgentConfig | None = None,
        output_schema: type | None = None,
        tools: list[Tool] | None = None,
        run_id: str | None = None,
    ) -> AgentResult[Any]:
        """Execute request synchronously with deadline and timeout enforcement."""
        resolved_config = config or self.config
        adapter = self.resolve_adapter(resolved_config)
        resolved_schema = output_schema or resolved_config.output_schema
        execution_id = run_id or str(uuid.uuid4())
        model = resolved_config.model or "default"

        if resolved_config.log_content:
            logger.debug("Starting execution run %s on model %s", execution_id, model)
        else:
            logger.debug(
                "Starting execution run %s (content logging disabled)", execution_id
            )

        tool_specs = [t.to_dict() for t in tools] if tools else []
        tool_map = {t.name: t for t in tools} if tools else {}

        request = ModelRequest(
            messages=list(messages),
            model=model,
            temperature=resolved_config.temperature,
            max_tokens=resolved_config.max_tokens,
            output_schema=resolved_schema,
            tools=tool_specs,
            extra_options=resolved_config.extra_options,
        )

        start_time = time.perf_counter()
        timeout = resolved_config.timeout
        deadline = start_time + timeout if timeout and timeout > 0 else None

        retries = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        max_tool_iterations = 5
        tool_iterations = 0

        while True:
            if deadline and time.perf_counter() > deadline:
                raise ProviderTimeoutError(
                    f"Agent execution timed out after {timeout}s.",
                    provider=resolved_config.provider,
                )

            try:
                # If deadline exists, run adapter with remaining timeout
                if deadline:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        raise ProviderTimeoutError(
                            f"Agent execution timed out after {timeout}s.",
                            provider=resolved_config.provider,
                        )
                    with concurrent.futures.ThreadPoolExecutor(
                        max_workers=1
                    ) as executor:
                        future = executor.submit(adapter.generate, request)
                        try:
                            response = future.result(timeout=remaining)
                        except concurrent.futures.TimeoutError as err:
                            raise ProviderTimeoutError(
                                f"Agent execution timed out after {timeout}s.",
                                provider=resolved_config.provider,
                            ) from err
                else:
                    response = adapter.generate(request)

                total_prompt_tokens += response.usage.prompt_tokens
                total_completion_tokens += response.usage.completion_tokens

                # Check if model requested tool calls
                if response.tool_calls:
                    if tool_iterations >= max_tool_iterations:
                        raise WorkflowLimitError(
                            f"Exceeded maximum permitted tool call iterations ({max_tool_iterations}). Runaway loop prevented."
                        )

                    tool_iterations += 1
                    request.messages.append(
                        ChatMessage(
                            role="assistant",
                            content=response.content or "",
                        )
                    )
                    for tc in response.tool_calls:
                        if tc.name in tool_map:
                            tool_inst = tool_map[tc.name]
                            tool_out = tool_inst.execute(tc.arguments)
                            request.messages.append(
                                ChatMessage(
                                    role="tool",
                                    content=json.dumps(tool_out)
                                    if not isinstance(tool_out, str)
                                    else tool_out,
                                    name=tc.name,
                                    tool_call_id=tc.id,
                                )
                            )
                    continue

                break
            except RateLimitError:
                retries += 1
                if retries > resolved_config.max_retries:
                    raise
                backoff = min(2.0**retries, 10.0)
                if deadline and (time.perf_counter() + backoff > deadline):
                    raise ProviderTimeoutError(
                        f"Agent execution timed out during rate limit retry after {timeout}s.",
                        provider=resolved_config.provider,
                    )
                time.sleep(backoff)
            except Exception:
                raise

        duration = time.perf_counter() - start_time

        final_output: Any = response.content
        if resolved_schema and issubclass(resolved_schema, BaseModel):
            final_output = self._parse_structured_output(
                response.content, resolved_schema
            )

        usage = UsageInfo(
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            total_tokens=total_prompt_tokens + total_completion_tokens,
        )

        return AgentResult(
            output=final_output,
            run_id=execution_id,
            model=response.model or model,
            duration=duration,
            usage=usage,
            metadata={"tool_iterations": tool_iterations},
        )

    async def aexecute(
        self,
        messages: list[ChatMessage],
        config: AgentConfig | None = None,
        output_schema: type | None = None,
        tools: list[Tool] | None = None,
        run_id: str | None = None,
    ) -> AgentResult[Any]:
        """Execute request asynchronously with timeout enforcement."""
        resolved_config = config or self.config
        adapter = self.resolve_adapter(resolved_config)
        resolved_schema = output_schema or resolved_config.output_schema
        execution_id = run_id or str(uuid.uuid4())
        model = resolved_config.model or "default"

        tool_specs = [t.to_dict() for t in tools] if tools else []
        tool_map = {t.name: t for t in tools} if tools else {}

        request = ModelRequest(
            messages=list(messages),
            model=model,
            temperature=resolved_config.temperature,
            max_tokens=resolved_config.max_tokens,
            output_schema=resolved_schema,
            tools=tool_specs,
            extra_options=resolved_config.extra_options,
        )

        start_time = time.perf_counter()
        timeout = resolved_config.timeout
        deadline = start_time + timeout if timeout and timeout > 0 else None

        retries = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        max_tool_iterations = 5
        tool_iterations = 0

        while True:
            if deadline and time.perf_counter() > deadline:
                raise ProviderTimeoutError(
                    f"Agent execution timed out after {timeout}s.",
                    provider=resolved_config.provider,
                )

            try:
                if deadline:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        raise ProviderTimeoutError(
                            f"Agent execution timed out after {timeout}s.",
                            provider=resolved_config.provider,
                        )
                    try:
                        response = await asyncio.wait_for(
                            adapter.agenerate(request), timeout=remaining
                        )
                    except TimeoutError as err:
                        raise ProviderTimeoutError(
                            f"Agent execution timed out after {timeout}s.",
                            provider=resolved_config.provider,
                        ) from err
                else:
                    response = await adapter.agenerate(request)

                total_prompt_tokens += response.usage.prompt_tokens
                total_completion_tokens += response.usage.completion_tokens

                if response.tool_calls:
                    if tool_iterations >= max_tool_iterations:
                        raise WorkflowLimitError(
                            f"Exceeded maximum permitted tool call iterations ({max_tool_iterations}). Runaway loop prevented."
                        )

                    tool_iterations += 1
                    request.messages.append(
                        ChatMessage(
                            role="assistant",
                            content=response.content or "",
                        )
                    )
                    for tc in response.tool_calls:
                        if tc.name in tool_map:
                            tool_inst = tool_map[tc.name]
                            tool_out = tool_inst.execute(tc.arguments)
                            request.messages.append(
                                ChatMessage(
                                    role="tool",
                                    content=json.dumps(tool_out)
                                    if not isinstance(tool_out, str)
                                    else tool_out,
                                    name=tc.name,
                                    tool_call_id=tc.id,
                                )
                            )
                    continue

                break
            except RateLimitError:
                retries += 1
                if retries > resolved_config.max_retries:
                    raise
                backoff = min(2.0**retries, 10.0)
                if deadline and (time.perf_counter() + backoff > deadline):
                    raise ProviderTimeoutError(
                        f"Agent execution timed out during rate limit retry after {timeout}s.",
                        provider=resolved_config.provider,
                    )
                await asyncio.sleep(backoff)
            except Exception:
                raise

        duration = time.perf_counter() - start_time

        final_output: Any = response.content
        if resolved_schema and issubclass(resolved_schema, BaseModel):
            final_output = self._parse_structured_output(
                response.content, resolved_schema
            )

        usage = UsageInfo(
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            total_tokens=total_prompt_tokens + total_completion_tokens,
        )

        return AgentResult(
            output=final_output,
            run_id=execution_id,
            model=response.model or model,
            duration=duration,
            usage=usage,
            metadata={"tool_iterations": tool_iterations},
        )
