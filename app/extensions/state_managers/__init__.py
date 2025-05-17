from .dummy_state_manager import DummyStateManager
from ...registries.state_managers import STATE_MANAGER_REGISTRY

STATE_MANAGER_REGISTRY.register("dummy", DummyStateManager)

__all__ = ["DummyStateManager"]
