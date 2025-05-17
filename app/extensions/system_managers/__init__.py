from .dummy_system_manager import DummySystemManager
from .system_manager import SystemManager
from ...registries.system_managers import SYSTEM_MANAGER_REGISTRY

SYSTEM_MANAGER_REGISTRY.register("dummy", DummySystemManager)
SYSTEM_MANAGER_REGISTRY.register("system", SystemManager)

__all__ = ["DummySystemManager", "SystemManager"]
