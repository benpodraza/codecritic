from .dummy_scoring_provider import DummyScoringProvider
from .basic_scoring_provider import BasicScoringProvider
from .advanced_scoring_provider import AdvancedScoringProvider
from ...registries.scoring_models import SCORING_MODEL_REGISTRY

SCORING_MODEL_REGISTRY.register("dummy", DummyScoringProvider)
SCORING_MODEL_REGISTRY.register("basic", BasicScoringProvider)
SCORING_MODEL_REGISTRY.register("advanced", AdvancedScoringProvider)

__all__ = [
    "DummyScoringProvider",
    "BasicScoringProvider",
    "AdvancedScoringProvider",
]
