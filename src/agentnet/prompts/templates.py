"""Prompt templates and validation."""

from __future__ import annotations

import string
from typing import Any

from agentnet.exceptions import ValidationError


class PromptTemplate:
    """Template for formatting model instructions with validated variable substitution."""

    def __init__(
        self, template: str, required_variables: list[str] | None = None
    ) -> None:
        self.template = template
        self._parsed_variables = self._extract_variables(template)
        self.required_variables = set(required_variables or self._parsed_variables)

    @classmethod
    def _extract_variables(cls, text: str) -> set[str]:
        formatter = string.Formatter()
        return {
            field_name
            for _, field_name, _, _ in formatter.parse(text)
            if field_name is not None
        }

    def format(self, **kwargs: Any) -> str:
        """Substitute variables into the template, raising ValidationError if any are missing."""
        missing = [v for v in self.required_variables if v not in kwargs]
        if missing:
            raise ValidationError(
                f"Missing required prompt variables: {', '.join(missing)}",
                details={"missing": missing},
            )
        try:
            return self.template.format(**kwargs)
        except KeyError as err:
            raise ValidationError(f"Missing template variable: {err}") from err
