from .dummy_scoring_provider import DummyScoringProvider
from .basic_scoring_provider import BasicScoringProvider
from ...registries.scoring_models import SCORING_MODEL_REGISTRY

SCORING_MODEL_REGISTRY.register("dummy", DummyScoringProvider)
SCORING_MODEL_REGISTRY.register("basic", BasicScoringProvider)

__all__ = ["DummyScoringProvider", "BasicScoringProvider"]
