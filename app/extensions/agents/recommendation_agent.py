from __future__ import annotations

from typing import List

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...factories.logging_provider import (
    ConversationLog,
    CodeQualityLog,
    ScoringLog,
    ErrorLog,
    RecommendationLog,
    LoggingProvider,
)
from ...utilities.snapshots.snapshot_writer import SnapshotWriter


class RecommendationAgent(AgentBase):
    """Analyze historical logs and generate code improvement recommendations."""

    def __init__(
        self,
        target: str,
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
    ) -> None:
        super().__init__(logger)
        self.target = target
        self.snapshot_writer = snapshot_writer or SnapshotWriter()
        self.recommendation_logs: List[RecommendationLog] = []
        self.error_logs: List[ErrorLog] = []

    def _run_agent_logic(self, *args, **kwargs) -> None:
        conv_logs: List[ConversationLog] = kwargs.get("conversation_log", [])
        qual_logs: List[CodeQualityLog] = kwargs.get("code_quality_log", [])
        scoring_logs: List[ScoringLog] = kwargs.get("scoring_log", [])

        recommendations: List[str] = []
        context_parts: List[str] = []

        for qlog in qual_logs:
            if qlog.lint_errors > 0:
                recommendations.append("Fix lint errors")
                context_parts.append("lint issues detected")
            if qlog.maintainability_index < 70:
                recommendations.append("Refactor to improve maintainability")
                context_parts.append("low maintainability")
            if qlog.cyclomatic_complexity > 10:
                recommendations.append("Simplify to reduce complexity")
                context_parts.append("high complexity")

        for slog in scoring_logs:
            if slog.value < 0.5:
                recommendations.append(f"Improve score for {slog.metric.value}")
                context_parts.append(f"low score {slog.metric.value}")

        for clog in conv_logs:
            if clog.intervention and clog.content:
                recommendations.append(clog.content)
                context_parts.append("prior intervention")

        unique = []
        for r in recommendations:
            if r not in unique:
                unique.append(r)

        if not unique:
            return

        rec_text = "; ".join(unique)
        ctx_text = "; ".join(context_parts)

        rec_log = RecommendationLog(
            experiment_id="exp",
            round=0,
            symbol=self.target,
            file_path=self.target,
            line_start=0,
            line_end=0,
            recommendation=rec_text,
            context=ctx_text,
        )
        self.recommendation_logs.append(rec_log)

        try:
            self.log_recommendation(rec_log)
        except Exception as exc:  # pragma: no cover - db failure
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.log_error(err)

        before = ctx_text
        after = rec_text
        self.snapshot_writer.write_snapshot(
            experiment_id="exp",
            round=0,
            file_path=self.target,
            before=before,
            after=after,
            symbol=self.target,
            agent_role=AgentRole.RECOMMENDER,
        )
