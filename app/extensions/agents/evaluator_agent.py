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
            ruff_proc = self.ruff.run(self.target)
            complexity = 0.0
            try:
                radon_proc = self.radon.run(self.target)
                if radon_proc.stdout:
                    for line in radon_proc.stdout.splitlines():
                        if "Complexity:" in line:
                            part = line.split("Complexity:")[-1].strip()
                            try:
                                complexity = float(part)
                            except ValueError:
                                pass
                            break
            except Exception as exc:  # pragma: no cover - optional
                self.logger.warning("Radon unavailable: %s", exc)
            lines = sum(1 for _ in open(self.target, "r"))
            log = CodeQualityLog(
                experiment_id="exp",
                round=0,
                symbol=self.target,
                lines_of_code=lines,
                cyclomatic_complexity=complexity,
                maintainability_index=0.0,
                lint_errors=0 if ruff_proc.returncode == 0 else 1,
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
