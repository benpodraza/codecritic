from __future__ import annotations

from typing import List

from ...abstract_classes.agent_base import AgentBase
from ...factories.tool_provider import ToolProviderFactory
from ...utilities.metadata.logging import CodeQualityLog, ErrorLog


class EvaluatorAgent(AgentBase):
    """Agent running static analysis and linting tools."""

    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target
        self.mypy = ToolProviderFactory.create("mypy")
        self.ruff = ToolProviderFactory.create("ruff")
        self.radon = ToolProviderFactory.create("radon")
        self.quality_logs: List[CodeQualityLog] = []
        self.error_logs: List[ErrorLog] = []

    def _run_agent_logic(
        self, *args, **kwargs
    ) -> None:  # pragma: no cover - simple logging
        try:
            self.mypy.run(self.target)
            self.ruff.run(self.target)
            try:
                self.radon.run(self.target)
            except Exception as exc:  # pragma: no cover - optional
                self.logger.warning("Radon unavailable: %s", exc)
            lines = sum(1 for _ in open(self.target, "r"))
            log = CodeQualityLog(
                experiment_id="exp",
                round=0,
                symbol=self.target,
                lines_of_code=lines,
                cyclomatic_complexity=0.0,
                maintainability_index=0.0,
                lint_errors=0,
            )
            self.quality_logs.append(log)
        except Exception as exc:  # pragma: no cover - safety
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.logger.exception("Evaluation failed for %s", self.target)
