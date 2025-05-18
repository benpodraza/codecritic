from .dummy_agent import DummyAgent
from .generator_agent import GeneratorAgent
from .evaluator_agent import EvaluatorAgent
from .mediator_agent import MediatorAgent
from ...registries.agents import AGENT_REGISTRY

AGENT_REGISTRY.register("dummy", DummyAgent)
AGENT_REGISTRY.register("generator", GeneratorAgent)
AGENT_REGISTRY.register("evaluator", EvaluatorAgent)
AGENT_REGISTRY.register("mediator", MediatorAgent)

__all__ = ["DummyAgent", "GeneratorAgent", "EvaluatorAgent", "MediatorAgent"]
