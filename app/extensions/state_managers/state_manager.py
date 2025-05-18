from __future__ import annotations

from ...abstract_classes.state_manager_base import StateManagerBase
from ...factories.logging_provider import LoggingProvider


class StateManager(StateManagerBase):
    """Concrete manager executing actions within each FSM state."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def _run_state_logic(self, *args, **kwargs) -> None:
        state = kwargs.get("state")
        self._log.info("Running state logic for %s", state)
