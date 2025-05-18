from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from ..factories.logging_provider import LoggingMixin, LoggingProvider, ScoringLog
from ..enums.scoring_enums import ScoringMetric


class ScoringModelBase(LoggingMixin, ABC):
    """Base class for more granular scoring models."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def score(self, experiment_id: str, *args, **kwargs) -> Dict[str, float]:
        self._log.debug("Scoring start")
        result = self._score(experiment_id, *args, **kwargs)
        self._log.debug("Scoring end")
        return result

    @abstractmethod
    def _score(self, experiment_id: str, *args, **kwargs) -> Dict[str, float]:
        """Compute evaluation metrics."""
        raise NotImplementedError

    def _log_metric(
        self, experiment_id: str, metric: ScoringMetric, value: float
    ) -> None:
        self.log_scoring(
            ScoringLog(
                experiment_id=experiment_id,
                round=0,
                metric=metric,
                value=value,
            )
        )
