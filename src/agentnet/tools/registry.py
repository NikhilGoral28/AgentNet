"""Tool registry for managing agent capabilities."""

from __future__ import annotations

from typing import Any

from agentnet.exceptions import ConfigurationError
from agentnet.tools.base import Tool


class ToolRegistry:
    """Registry managing available tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Retrieve a registered tool by name."""
        if name not in self._tools:
            raise ConfigurationError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def to_schemas(self) -> list[dict[str, Any]]:
        """Export tool specifications for model requests."""
        return [tool.to_dict() for tool in self._tools.values()]
