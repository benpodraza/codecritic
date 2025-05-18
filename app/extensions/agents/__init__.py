from .dummy_agent import DummyAgent
from .generator_agent import GeneratorAgent
from .evaluator_agent import EvaluatorAgent
from .mediator_agent import MediatorAgent
from .patch_agent import PatchAgent
from .recommendation_agent import RecommendationAgent
from ...registries.agents import AGENT_REGISTRY

AGENT_REGISTRY.register("dummy", DummyAgent)
AGENT_REGISTRY.register("generator", GeneratorAgent)
AGENT_REGISTRY.register("evaluator", EvaluatorAgent)
AGENT_REGISTRY.register("mediator", MediatorAgent)
AGENT_REGISTRY.register("patch", PatchAgent)
AGENT_REGISTRY.register("recommendation", RecommendationAgent)

__all__ = [
    "DummyAgent",
    "GeneratorAgent",
    "EvaluatorAgent",
    "MediatorAgent",
    "PatchAgent",
    "RecommendationAgent",
]
