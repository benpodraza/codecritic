from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..factories.scoring_provider import ScoringProviderFactory


class Experiment:
    """Base experiment handling execution and scoring."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.scoring_model_id = config.get("scoring_model_id", "dummy")

        self.evaluation_logs: List[Any] = []
        self.code_quality_logs: List[Any] = []
        self.conversation_logs: List[Any] = []
        self.prompt_logs: List[Any] = []
        self.state_logs: List[Any] = []

    def run(self, *args, **kwargs) -> Dict[str, float]:
        self.logger.debug("Experiment run start")
        self._run_experiment_logic(*args, **kwargs)
        self.logger.debug("Experiment run end")

        logs = {
            "evaluation": self.evaluation_logs,
            "code_quality": self.code_quality_logs,
            "conversation": self.conversation_logs,
            "prompt": self.prompt_logs,
            "state": self.state_logs,
        }
        scoring_provider = ScoringProviderFactory.create(self.scoring_model_id)
        metrics = scoring_provider.score(logs)
        self.logger.info("Experiment metrics: %s", metrics)
        return metrics

    def _run_experiment_logic(self, *args, **kwargs) -> None:
        """Override to implement experiment steps."""
        raise NotImplementedError
