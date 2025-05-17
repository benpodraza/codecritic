from .dummy_system_manager import DummySystemManager
from ...registries.system_managers import SYSTEM_MANAGER_REGISTRY

SYSTEM_MANAGER_REGISTRY.register("dummy", DummySystemManager)

__all__ = ["DummySystemManager"]
