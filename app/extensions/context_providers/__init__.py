from .dummy_context_provider import DummyContextProvider
from ...db.seeders.files.symbol_graph import SymbolGraphProvider
from ...registries.context_providers import CONTEXT_PROVIDER_REGISTRY

CONTEXT_PROVIDER_REGISTRY.register("dummy", DummyContextProvider)
CONTEXT_PROVIDER_REGISTRY.register("symbol_graph", SymbolGraphProvider)

__all__ = ["DummyContextProvider", "SymbolGraphProvider"]
