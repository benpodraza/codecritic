from .. import Registry

SYSTEM_MANAGER_REGISTRY = Registry()

try:  # pragma: no cover - optional seed import
    from ...extensions.system_managers.dummy_system_manager import (
        DummySystemManager,
    )

    SYSTEM_MANAGER_REGISTRY.register("dummy", DummySystemManager)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
