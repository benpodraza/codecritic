from .dummy_scoring_provider import DummyScoringProvider
from ...registries.scoring_models import SCORING_MODEL_REGISTRY

SCORING_MODEL_REGISTRY.register("dummy", DummyScoringProvider)

__all__ = ["DummyScoringProvider"]
