from __future__ import annotations

from typing import Any, Dict, List

from .advanced_scoring_provider import AdvancedScoringProvider
from ...utilities.feedback import FeedbackRepository
from ...factories.logging_provider import LoggingProvider


class AdaptiveScoringProvider(AdvancedScoringProvider):
    """Scoring provider that adjusts weights based on feedback."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)
        self.weights: Dict[str, float] = {
            "maintainability_index": 1.0,
            "cyclomatic_complexity": 1.0,
            "recommendation_quality": 1.0,
        }

    def _score(
        self, logs: Dict[str, List[Any]], experiment_id: str = "exp"
    ) -> Dict[str, float]:
        metrics = super()._score(logs, experiment_id)

        for fb in FeedbackRepository.get_feedback(experiment_id):
            text = fb.feedback.lower()
            if "maintainability" in text:
                self.weights["maintainability_index"] += 0.1
            if "complexity" in text:
                self.weights["cyclomatic_complexity"] += 0.1
            if "recommendation" in text:
                self.weights["recommendation_quality"] += 0.1

        weighted = {
            key: value * self.weights.get(key, 1.0) for key, value in metrics.items()
        }
        return weighted
