from .dummy_context_provider import DummyContextProvider
from ...registries.context_providers import CONTEXT_PROVIDER_REGISTRY

CONTEXT_PROVIDER_REGISTRY.register("dummy", DummyContextProvider)

__all__ = ["DummyContextProvider"]
