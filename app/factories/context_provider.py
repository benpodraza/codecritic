from __future__ import annotations

from ..registries.context_providers import CONTEXT_PROVIDER_REGISTRY


class ContextProviderFactory:
    @staticmethod
    def create(name: str, **kwargs):
        cls = CONTEXT_PROVIDER_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"Context provider {name} not registered")
        return cls(**kwargs)
