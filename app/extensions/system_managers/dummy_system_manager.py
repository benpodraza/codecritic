from ...abstract_classes.system_manager_base import SystemManagerBase


class DummySystemManager(SystemManagerBase):
    def _run_system_logic(self, *args, **kwargs) -> None:
        self._log.info("Dummy system logic executed")
