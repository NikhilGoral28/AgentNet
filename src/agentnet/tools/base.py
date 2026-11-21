"""Tool definitions and contracts."""

from __future__ import annotations

import concurrent.futures
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, create_model

from agentnet.exceptions import (
    ToolError,
    ToolPermissionError,
    ToolTimeoutError,
    ValidationError,
)


@dataclass
class Tool:
    """A callable capability available to agents with validation and permission checks."""

    name: str
    description: str
    function: Callable[..., Any]
    input_schema: type[BaseModel] | None = None
    requires_approval: bool = False
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if self.input_schema is None:
            self.input_schema = self._infer_schema(self.function)

    @classmethod
    def _infer_schema(cls, fn: Callable[..., Any]) -> type[BaseModel]:
        """Infer a Pydantic schema from function type hints."""
        sig = inspect.signature(fn)
        fields: dict[str, Any] = {}
        for param in sig.parameters.values():
            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            annotation = (
                param.annotation
                if param.annotation is not inspect.Parameter.empty
                else Any
            )
            default = (
                param.default if param.default is not inspect.Parameter.empty else ...
            )
            fields[param.name] = (annotation, default)

        return create_model(f"{fn.__name__}_Schema", **fields)

    def to_dict(self) -> dict[str, Any]:
        """Export tool definition in OpenAI-compatible format."""
        parameters = {}
        if self.input_schema and issubclass(self.input_schema, BaseModel):
            parameters = self.input_schema.model_json_schema()

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": parameters,
            },
        }

    def execute(
        self, arguments: dict[str, Any] | None = None, is_approved: bool = False
    ) -> Any:
        """Validate arguments, check permissions, and execute the tool with timeout enforcement."""
        args = arguments or {}

        if self.requires_approval and not is_approved:
            raise ToolPermissionError(
                f"Tool '{self.name}' requires explicit application approval to execute.",
                tool_name=self.name,
            )

        if self.input_schema:
            try:
                validated = self.input_schema(**args)
                args = validated.model_dump()
            except Exception as err:
                raise ValidationError(
                    f"Invalid arguments for tool '{self.name}': {err}",
                    details={"tool": self.name, "errors": str(err)},
                ) from err

        def _run() -> Any:
            return self.function(**args)

        if self.timeout and self.timeout > 0:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run)
                try:
                    return future.result(timeout=self.timeout)
                except concurrent.futures.TimeoutError as err:
                    raise ToolTimeoutError(
                        f"Tool '{self.name}' timed out after {self.timeout}s.",
                        tool_name=self.name,
                    ) from err
                except Exception as err:
                    raise ToolError(
                        f"Execution failed for tool '{self.name}': {err}",
                        tool_name=self.name,
                    ) from err
        else:
            try:
                return _run()
            except Exception as err:
                raise ToolError(
                    f"Execution failed for tool '{self.name}': {err}",
                    tool_name=self.name,
                ) from err

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Direct invocation shortcut."""
        return self.function(*args, **kwargs)
