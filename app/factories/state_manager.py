from __future__ import annotations

from ..registries.state_managers import STATE_MANAGER_REGISTRY


class StateManagerFactory:
    @staticmethod
    def register(name: str, cls) -> None:
        try:
            STATE_MANAGER_REGISTRY.register(name, cls)
        except KeyError:
            pass

    @staticmethod
    def create(name: str, **kwargs):
        cls = STATE_MANAGER_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"State manager {name} not registered")
        return cls(**kwargs)
