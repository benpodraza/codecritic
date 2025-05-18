from __future__ import annotations

from typing import Any, Dict, List

from ...abstract_classes.scoring_provider_base import ScoringProviderBase
from ...utilities.metrics import compute_metrics


class BasicScoringProvider(ScoringProviderBase):
    """Compute experiment metrics using basic heuristics."""

    def _score(self, logs: Dict[str, List[Any]]) -> Dict[str, float]:
        self.logger.debug("Scoring with logs: %s", logs)
        evaluation_logs = logs.get("evaluation", [])
        code_quality_logs = logs.get("code_quality", [])
        conversation_logs = logs.get("conversation", [])
        prompt_logs = logs.get("prompt", [])
        state_logs = logs.get("state", [])

        metrics = compute_metrics(
            evaluation_logs,
            code_quality_logs,
            conversation_logs,
            prompt_logs,
            state_logs,
        )
        self.logger.info("Computed metrics: %s", metrics)
        return metrics
