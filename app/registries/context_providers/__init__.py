from .. import Registry

CONTEXT_PROVIDER_REGISTRY = Registry()

try:  # pragma: no cover - optional seed import
    from ...extensions.context_providers.dummy_context_provider import (
        DummyContextProvider,
    )

    CONTEXT_PROVIDER_REGISTRY.register("dummy", DummyContextProvider)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
