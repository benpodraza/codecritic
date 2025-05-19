from __future__ import annotations

from datetime import datetime, timezone

from app.factories.logging_provider import LoggingMixin, LoggingProvider
from app.utilities.metadata.logging.log_schemas import ExperimentLog, SystemEventLog


class ExperimentProvider(LoggingMixin):
    """Manage experiment lifecycle and logging."""

    def __init__(
        self,
        experiment_id: str,
        description: str,
        mode: str,
        variant: str,
        max_iterations: int,
        stop_threshold: float,
        model_engine: str,
        evaluator_name: str,
        evaluator_version: str,
        logger: LoggingProvider | None = None,
    ) -> None:
        super().__init__(logger)
        self.experiment_id = experiment_id
        self.description = description
        self.mode = mode
        self.variant = variant
        self.max_iterations = max_iterations
        self.stop_threshold = stop_threshold
        self.model_engine = model_engine
        self.evaluator_name = evaluator_name
        self.evaluator_version = evaluator_version
        self.start_time = datetime.now(timezone.utc)
        self.logger.log_system_event(
            SystemEventLog(
                experiment_id=experiment_id,
                round=0,
                system_id=self.__class__.__name__,
                event="start",
                details="",
                success=True,
                error_message=None,
                timestamp=self.start_time,
            )
        )

    def complete(self, final_score: float, passed: bool, reason: str) -> None:
        self.logger.log_experiment(
            ExperimentLog(
                experiment_id=self.experiment_id,
                description=self.description,
                mode=self.mode,
                variant=self.variant,
                max_iterations=self.max_iterations,
                stop_threshold=self.stop_threshold,
                model_engine=self.model_engine,
                evaluator_name=self.evaluator_name,
                evaluator_version=self.evaluator_version,
                final_score=final_score,
                passed=passed,
                reason_for_stop=reason,
                start=self.start_time,
                stop=datetime.now(timezone.utc),
            )
        )
