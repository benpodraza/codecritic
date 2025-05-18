from ...abstract_classes.state_manager_base import StateManagerBase


class DummyStateManager(StateManagerBase):
    def _run_state_logic(self, *args, **kwargs) -> None:
        self._log.info("Dummy state logic executed")
