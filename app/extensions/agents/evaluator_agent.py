from __future__ import annotations

from pathlib import Path
from typing import List

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...factories.tool_provider import ToolProviderFactory
from ...factories.logging_provider import (
    CodeQualityLog,
    ErrorLog,
    LoggingProvider,
)
from ...utilities.snapshots.snapshot_writer import SnapshotWriter


def _analyze_radon(code: str) -> tuple[float, float]:
    """Return cyclomatic complexity and maintainability index for the code."""
    try:
        from radon.complexity import cc_visit
        from radon.metrics import mi_visit

        blocks = cc_visit(code)
        cc = sum(b.complexity for b in blocks) / max(len(blocks), 1)
        mi = mi_visit(code, True)
        return float(cc), float(mi)
    except Exception:
        return 0.0, 0.0


class EvaluatorAgent(AgentBase):
    """Run static analysis tools and log code quality metrics."""

    def __init__(
        self,
        target: str,
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
    ) -> None:
        super().__init__(logger)
        self.target = target
        self.snapshot_writer = snapshot_writer or SnapshotWriter()
        self.mypy = ToolProviderFactory.create("mypy")
        self.ruff = ToolProviderFactory.create("ruff")
        self.black = ToolProviderFactory.create("black")
        self.radon = ToolProviderFactory.create("radon")
        self.quality_logs: List[CodeQualityLog] = []
        self.error_logs: List[ErrorLog] = []

    def _run_agent_logic(self, *args, **kwargs) -> None:
        before = Path(self.target).read_text(encoding="utf-8")
        lines = len(before.splitlines())
        complexity = 0.0
        maintainability = 0.0
        lint_return = 0

        try:
            self.mypy.run(self.target)
        except Exception as exc:  # pragma: no cover - tool execution failure
            self.error_logs.append(
                ErrorLog(
                    experiment_id="exp",
                    round=0,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    file_path=self.target,
                )
            )

        try:
            ruff_proc = self.ruff.run(self.target)
            lint_return = ruff_proc.returncode
        except Exception as exc:  # pragma: no cover - tool execution failure
            self.error_logs.append(
                ErrorLog(
                    experiment_id="exp",
                    round=0,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    file_path=self.target,
                )
            )
            lint_return = 1

        try:
            self.black.run(self.target, check=True)
        except Exception as exc:  # pragma: no cover - tool execution failure
            self.error_logs.append(
                ErrorLog(
                    experiment_id="exp",
                    round=0,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    file_path=self.target,
                )
            )

        try:
            # Run radon CLI primarily for logging/debug purposes
            self.radon.run(self.target)
            complexity, maintainability = _analyze_radon(before)
        except Exception as exc:
            self._log.warning("Radon unavailable: %s", exc)

        log = CodeQualityLog(
            experiment_id="exp",
            round=0,
            symbol=self.target,
            lines_of_code=lines,
            cyclomatic_complexity=complexity,
            maintainability_index=maintainability,
            lint_errors=0 if lint_return == 0 else 1,
        )
        self.quality_logs.append(log)
        self.log_code_quality(log)
        for err in self.error_logs:
            self.log_error(err)

        after = Path(self.target).read_text(encoding="utf-8")
        self.snapshot_writer.write_snapshot(
            experiment_id="exp",
            round=0,
            file_path=self.target,
            before=before,
            after=after,
            symbol=self.target,
            agent_role=AgentRole.EVALUATOR,
        )
