from .. import Registry

AGENT_REGISTRY = Registry()

# Seed registry with a default implementation so factories work without
# requiring explicit extension imports.
try:  # pragma: no cover - optional seed import
    from ...extensions.agents.dummy_agent import DummyAgent

    AGENT_REGISTRY.register("dummy", DummyAgent)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
