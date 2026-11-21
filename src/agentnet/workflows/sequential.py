"""SequentialWorkflow implementation."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from typing import Any

from agentnet.core.base import BaseAgent
from agentnet.core.results import AgentResult, UsageInfo
from agentnet.exceptions import WorkflowLimitError, WorkflowStepError


class SequentialWorkflow:
    """Executes a defined sequence of agents or callable steps with bounded limits."""

    def __init__(
        self,
        steps: list[BaseAgent[Any] | tuple[str, BaseAgent[Any]]],
        step_mappings: dict[str, Callable[[dict[str, Any]], dict[str, Any]]]
        | None = None,
        max_steps: int = 50,
        timeout: float | None = None,
    ) -> None:
        self.step_list: list[tuple[str, BaseAgent[Any]]] = []
        for i, item in enumerate(steps):
            if isinstance(item, tuple):
                self.step_list.append(item)
            else:
                self.step_list.append((f"step_{i + 1}", item))

        if len(self.step_list) > max_steps:
            raise WorkflowLimitError(
                f"Workflow exceeded maximum allowed step count ({len(self.step_list)} > {max_steps})."
            )

        self.step_mappings = step_mappings or {}
        self.max_steps = max_steps
        self.timeout = timeout

    def run(self, **initial_inputs: Any) -> AgentResult[Any]:
        """Execute all workflow steps in sequence with timeout enforcement."""
        run_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        deadline = (
            start_time + self.timeout if self.timeout and self.timeout > 0 else None
        )
        state: dict[str, Any] = dict(initial_inputs)
        step_results: dict[str, AgentResult[Any]] = {}

        total_prompt_tokens = 0
        total_completion_tokens = 0
        last_output: Any = None
        last_model: str = "workflow"

        for step_name, agent in self.step_list:
            if deadline and time.perf_counter() > deadline:
                raise WorkflowLimitError(
                    f"Workflow execution timed out after {self.timeout}s at step '{step_name}'."
                )
            if step_name in self.step_mappings:
                step_inputs = self.step_mappings[step_name](state)
            else:
                # Default: pass state values matching agent parameters, or previous output if single text
                step_inputs = state

            try:
                res = agent.run(**step_inputs)
                step_results[step_name] = res
                state[step_name] = res
                last_output = res.output
                last_model = res.model
                total_prompt_tokens += res.usage.prompt_tokens
                total_completion_tokens += res.usage.completion_tokens
            except Exception as err:
                raise WorkflowStepError(
                    f"Workflow failed at step '{step_name}': {err}",
                    step_id=step_name,
                ) from err

        duration = time.perf_counter() - start_time
        usage = UsageInfo(
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            total_tokens=total_prompt_tokens + total_completion_tokens,
        )

        return AgentResult(
            output=last_output,
            run_id=run_id,
            model=last_model,
            duration=duration,
            usage=usage,
            metadata={"steps": {k: v.output for k, v in step_results.items()}},
        )
