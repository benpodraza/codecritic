from .dummy_state_manager import DummyStateManager
from .state_manager import StateManager
from ...registries.state_managers import STATE_MANAGER_REGISTRY

STATE_MANAGER_REGISTRY.register("dummy", DummyStateManager)
STATE_MANAGER_REGISTRY.register("state", StateManager)

__all__ = ["DummyStateManager", "StateManager"]
