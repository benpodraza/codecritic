from __future__ import annotations

from ..registries.system_managers import SYSTEM_MANAGER_REGISTRY


class SystemManagerFactory:
    @staticmethod
    def create(name: str, **kwargs):
        cls = SYSTEM_MANAGER_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"System manager {name} not registered")
        return cls(**kwargs)
