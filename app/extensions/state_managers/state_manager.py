from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from ...abstract_classes.state_manager_base import StateManagerBase
from ...enums.system_enums import SystemState, StateTransitionReason
from ...factories.logging_provider import LoggingProvider
from ...utilities.metadata.logging.log_schemas import StateLog, StateTransitionLog


class StateManager(StateManagerBase):
    """Concrete manager executing actions within each FSM state."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)
        self.current_state = SystemState.START
        self.state_logs: List[StateLog] = []
        self.transition_logs: List[StateTransitionLog] = []

    def _run_state_logic(self, *args, **kwargs) -> None:
        state = kwargs.get("state")
        self._log.info("Running state logic for %s", state)

    def transition_state(
        self,
        experiment_id: str,
        round: int,
        from_state: SystemState,
        to_state: SystemState,
        reason: StateTransitionReason,
    ) -> None:
        """Log a state transition and update current state."""
        log = StateTransitionLog(
            experiment_id=experiment_id,
            round=round,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
        )
        self.transition_logs.append(log)
        self.log_transition(log)
        self._log.info("%s -> %s", from_state.value, to_state.value)
        self.current_state = to_state

    def run_state(
        self,
        experiment_id: str,
        system: str,
        round: int,
        state: SystemState,
        action: str,
        score: float | None = None,
        details: str | None = "",
    ) -> None:
        """Execute state logic and log the action."""
        self._run_state_logic(state=state)
        log = StateLog(
            experiment_id=experiment_id,
            system=system,
            round=round,
            state=state,
            action=action,
            score=score,
            details=details,
            timestamp=datetime.now(timezone.utc),
        )
        self.state_logs.append(log)
        self.log_state(log)
