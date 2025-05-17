from __future__ import annotations

from ..registries.scoring_models import SCORING_MODEL_REGISTRY


class ScoringProviderFactory:
    @staticmethod
    def create(name: str, **kwargs):
        cls = SCORING_MODEL_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"Scoring provider {name} not registered")
        return cls(**kwargs)
