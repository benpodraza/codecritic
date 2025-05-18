from __future__ import annotations

from typing import Dict, List

from ...abstract_classes.scoring_model_base import ScoringModelBase
from ...factories.logging_provider import RecommendationLog
from ...enums.scoring_enums import ScoringMetric


class RecommendationQualityScorer(ScoringModelBase):
    """Evaluate recommendations for context relevance."""

    def _score(
        self, experiment_id: str, logs: List[RecommendationLog]
    ) -> Dict[str, float]:
        if not logs:
            quality = 0.0
        else:
            with_context = [1.0 for log in logs if log.context]
            quality = sum(with_context) / len(logs)

        self._log_metric(experiment_id, ScoringMetric.RECOMMENDATION_QUALITY, quality)

        return {ScoringMetric.RECOMMENDATION_QUALITY.value: quality}
