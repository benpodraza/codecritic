from __future__ import annotations

from ...abstract_classes.state_manager_base import StateManagerBase


class StateManager(StateManagerBase):
    """Concrete manager executing actions within each FSM state."""

    def _run_state_logic(self, *args, **kwargs) -> None:
        state = kwargs.get("state")
        self.logger.info("Running state logic for %s", state)
