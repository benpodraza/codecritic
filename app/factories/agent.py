from __future__ import annotations

from ..registries.agents import AGENT_REGISTRY


class AgentFactory:
    @staticmethod
    def register(name: str, cls) -> None:
        try:
            AGENT_REGISTRY.register(name, cls)
        except KeyError:
            pass

    @staticmethod
    def create(name: str, **kwargs):
        cls = AGENT_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"Agent {name} not registered")
        return cls(**kwargs)
