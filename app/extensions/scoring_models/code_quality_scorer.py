from __future__ import annotations

from typing import Dict, List

from ...abstract_classes.scoring_model_base import ScoringModelBase
from ...factories.logging_provider import CodeQualityLog
from ...enums.scoring_enums import ScoringMetric


class CodeQualityScorer(ScoringModelBase):
    """Evaluate code quality logs and compute quality metrics."""

    def _score(
        self, experiment_id: str, logs: List[CodeQualityLog]
    ) -> Dict[str, float]:
        if not logs:
            mi = 0.0
            cc = 0.0
        else:
            mi = sum(log.maintainability_index for log in logs) / len(logs)
            cc = sum(log.cyclomatic_complexity for log in logs) / len(logs)

        self._log_metric(experiment_id, ScoringMetric.MAINTAINABILITY_INDEX, mi)
        self._log_metric(experiment_id, ScoringMetric.CYCLOMATIC_COMPLEXITY, cc)

        return {
            ScoringMetric.MAINTAINABILITY_INDEX.value: mi,
            ScoringMetric.CYCLOMATIC_COMPLEXITY.value: cc,
        }
