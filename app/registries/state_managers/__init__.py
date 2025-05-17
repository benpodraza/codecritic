from .. import Registry

STATE_MANAGER_REGISTRY = Registry()

try:  # pragma: no cover - optional seed import
    from ...extensions.state_managers.dummy_state_manager import DummyStateManager

    STATE_MANAGER_REGISTRY.register("dummy", DummyStateManager)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
