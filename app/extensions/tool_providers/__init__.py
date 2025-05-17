from .dummy_tool_provider import DummyToolProvider
from ...registries.tool_providers import TOOL_PROVIDER_REGISTRY

TOOL_PROVIDER_REGISTRY.register("dummy", DummyToolProvider)

__all__ = ["DummyToolProvider"]
