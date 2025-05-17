from .dummy_agent import DummyAgent
from ...registries.agents import AGENT_REGISTRY

AGENT_REGISTRY.register("dummy", DummyAgent)

__all__ = ["DummyAgent"]
