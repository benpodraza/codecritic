from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..factories.scoring_provider import ScoringProviderFactory
from ..factories.system_manager import SystemManagerFactory
from ..factories.experiment_config_provider import ExperimentConfigProvider
from ..utilities.db import init_db, insert_logs
from ..utilities.metadata.logging import ScoringLog
from ..utilities.metrics import EVALUATION_METRICS


class Experiment:
    """Base experiment handling execution and scoring."""

    def __init__(self, config_id: int) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
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
        self.logger.debug("Experiment run start")

        # load configuration
        self.config = ExperimentConfigProvider.load(self.config_id)
        self.scoring_model_id = self.config.get("scoring_model_id", "dummy")
        system_manager_id = self.config.get("system_manager_id", "dummy")

        # run system manager
        manager = SystemManagerFactory.create(system_manager_id)
        manager.run()

        # collect logs from manager
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

        scoring_provider = ScoringProviderFactory.create(self.scoring_model_id)
        metrics = scoring_provider.score(logs)
        for key in EVALUATION_METRICS:
            metrics.setdefault(key, 0.0)
        self.logger.info("Experiment metrics: %s", metrics)

        # persist scoring logs
        conn = init_db()
        scoring_logs = [
            ScoringLog(
                experiment_id="exp",
                round=0,
                metric=k,
                value=v,
            )
            for k, v in metrics.items()
        ]
        insert_logs(conn, "scoring_log", scoring_logs)
        conn.close()

        self.metrics = metrics
        self.logger.debug("Experiment run end")
        return metrics

    def _run_experiment_logic(self, *args, **kwargs) -> None:
        """Override to implement experiment steps."""
        raise NotImplementedError
