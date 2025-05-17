from .. import Registry

TOOL_PROVIDER_REGISTRY = Registry()

try:  # pragma: no cover - optional seed import
    from ...extensions.tool_providers.dummy_tool_provider import DummyToolProvider

    TOOL_PROVIDER_REGISTRY.register("dummy", DummyToolProvider)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
