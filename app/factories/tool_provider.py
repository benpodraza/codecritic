from __future__ import annotations

from ..registries.tool_providers import TOOL_PROVIDER_REGISTRY


class ToolProviderFactory:
    @staticmethod
    def register(name: str, cls) -> None:
        try:
            TOOL_PROVIDER_REGISTRY.register(name, cls)
        except KeyError:
            pass

    @staticmethod
    def create(name: str, **kwargs):
        cls = TOOL_PROVIDER_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"Tool provider {name} not registered")
        return cls(**kwargs)
