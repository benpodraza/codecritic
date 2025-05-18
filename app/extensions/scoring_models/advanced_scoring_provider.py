from __future__ import annotations

from typing import Any, Dict, List

from ...abstract_classes.scoring_provider_base import ScoringProviderBase
from .code_quality_scorer import CodeQualityScorer
from .recommendation_quality_scorer import RecommendationQualityScorer


class AdvancedScoringProvider(ScoringProviderBase):
    """Combine quality and recommendation scoring into a single provider."""

    def __init__(self, logger=None) -> None:
        super().__init__(logger)
        self.code_quality = CodeQualityScorer(logger)
        self.recommendation = RecommendationQualityScorer(logger)

    def _score(
        self, logs: Dict[str, List[Any]], experiment_id: str = "exp"
    ) -> Dict[str, float]:
        code_quality_logs = logs.get("code_quality", [])
        recommendation_logs = logs.get("recommendation", [])

        metrics: Dict[str, float] = {}
        metrics.update(self.code_quality.score(experiment_id, code_quality_logs))
        metrics.update(self.recommendation.score(experiment_id, recommendation_logs))
        return metrics
