from __future__ import annotations

from typing import List, Any

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...factories.logging_provider import (
    ConversationLog,
    ErrorLog,
    LoggingProvider,
)
from ...utilities.snapshots.snapshot_writer import SnapshotWriter


class MediatorAgent(AgentBase):
    """Agent that reconciles discrepancies between generator and evaluator outputs."""

    def __init__(
        self,
        target: str = "generated.py",
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
    ) -> None:
        super().__init__(logger)
        self.target = target
        self.snapshot_writer = snapshot_writer or SnapshotWriter()
        self.conversation_logs: List[ConversationLog] = []
        self.error_logs: List[ErrorLog] = []

    def _run_agent_logic(self, *args, **kwargs) -> None:
        code: str | None = kwargs.get("generator_output")
        metrics: dict[str, Any] | None = kwargs.get("evaluation_metrics")

        if code is None or metrics is None:
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type="ValueError",
                message="Missing generator output or evaluation metrics",
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.log_error(err)
            return

        lint_errors = int(metrics.get("lint_errors", 0))
        maintainability = float(metrics.get("maintainability_index", 100.0))
        complexity = float(metrics.get("cyclomatic_complexity", 0.0))

        recommendations: List[str] = []
        if lint_errors > 0:
            recommendations.append("Resolve lint errors")
        if maintainability < 70:
            recommendations.append("Increase maintainability")
        if complexity > 10:
            recommendations.append("Reduce complexity")

        rec_text = "; ".join(recommendations)
        conv = ConversationLog(
            experiment_id="exp",
            round=0,
            agent_role=AgentRole.MEDIATOR,
            target=self.target,
            content=rec_text,
            originating_agent="mediator",
            intervention=bool(recommendations),
            intervention_type="mediation" if recommendations else None,
            intervention_reason="evaluation discrepancy" if recommendations else None,
        )
        self.conversation_logs.append(conv)

        try:
            self.log_conversation(conv)
        except Exception as exc:  # pragma: no cover - db write failure
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.log_error(err)

        after = code
        if rec_text:
            after = code + f"\n# Mediator Recommendation: {rec_text}"

        self.snapshot_writer.write_snapshot(
            experiment_id="exp",
            round=0,
            file_path=self.target,
            before=code,
            after=after,
            symbol=self.target,
            agent_role=AgentRole.MEDIATOR,
        )
