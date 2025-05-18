from __future__ import annotations

from typing import Any, Dict, List

from ..factories.scoring_provider import ScoringProviderFactory
from ..factories.system_manager import SystemManagerFactory
from ..factories.experiment_config_provider import ExperimentConfigProvider
from ..utilities.metadata.logging import LoggingMixin, LoggingProvider, ScoringLog
from ..utilities.metrics import EVALUATION_METRICS


class Experiment(LoggingMixin):
    """Base experiment handling execution and scoring."""

    def __init__(self, config_id: int, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)
        self.config_id = config_id
        self.config: Dict[str, Any] | None = None
        self.scoring_model_id = "dummy"

        self.evaluation_logs: List[Any] = []
        self.code_quality_logs: List[Any] = []
        self.conversation_logs: List[Any] = []
        self.prompt_logs: List[Any] = []
        self.state_logs: List[Any] = []
        self.metrics: Dict[str, float] | None = None

        def run(self, *args, **kwargs) -> Dict[str, float]:
            self._log.debug("Experiment run start")

            #  load configuration
            self.config = ExperimentConfigProvider.load(self.config_id)
            self.scoring_model_id = self.config.get("scoring_model_id", "dummy")
            system_manager_id = self.config.get("system_manager_id", "dummy")

            #  run system manager *with* our injected logger
            manager = SystemManagerFactory.create(
                system_manager_id,
                logger=self.logger,
            )
            manager.run()

            #  collect logs from manager
            self.evaluation_logs = getattr(manager, "evaluation_logs", [])
            self.code_quality_logs = getattr(manager, "code_quality_logs", [])
            self.conversation_logs = getattr(manager, "conversation_logs", [])
            self.prompt_logs = getattr(manager, "prompt_logs", [])
            self.state_logs = getattr(manager, "state_logs", [])

            logs = {
                "evaluation": self.evaluation_logs,
                "code_quality": self.code_quality_logs,
                "conversation": self.conversation_logs,
                "prompt": self.prompt_logs,
                "state": self.state_logs,
            }

            scoring_provider = ScoringProviderFactory.create(
                self.scoring_model_id,
                logger=self.logger,
            )
            metrics = scoring_provider.score(logs)
            for key in EVALUATION_METRICS:
                metrics.setdefault(key, 0.0)
            self._log.info("Experiment metrics: %s", metrics)

            for k, v in metrics.items():
                self.log_scoring(
                    ScoringLog(
                        experiment_id=str(self.config_id),
                        round=0,
                        metric=k,
                        value=v,
                    )
                )

            self.metrics = metrics
            self._log.debug("Experiment run end")
            return metrics

    def _run_experiment_logic(self, *args, **kwargs) -> None:
        """Override to implement experiment steps."""
        raise NotImplementedError
