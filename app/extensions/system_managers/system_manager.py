from __future__ import annotations

from typing import List

from ...abstract_classes.system_manager_base import SystemManagerBase
from ...enums.system_enums import FSMState
from ...utilities.metadata.logging import StateTransitionLog
from ..state_managers.state_manager import StateManager


class SystemManager(SystemManagerBase):
    """Concrete system manager implementing FSM transitions."""

    def __init__(self) -> None:
        super().__init__()
        self.state_manager = StateManager()
        self.current_state = FSMState.START
        self.transition_logs: List[StateTransitionLog] = []

    def _transition_to(self, next_state: FSMState, reason: str | None = None) -> None:
        log = StateTransitionLog(
            experiment_id="exp",
            round=0,
            from_state=self.current_state.value,
            to_state=next_state.value,
            reason=reason,
        )
        self.transition_logs.append(log)
        self.logger.info("%s -> %s", self.current_state.value, next_state.value)
        self.current_state = next_state

    def _run_system_logic(self, *args, **kwargs) -> None:
        sequence = [
            FSMState.GENERATE,
            FSMState.DISCRIMINATE,
            FSMState.MEDIATE,
            FSMState.PATCHOR,
            FSMState.RECOMMENDER,
            FSMState.END,
        ]
        for state in sequence:
            self._transition_to(state)
            if state is not FSMState.END:
                self.state_manager.run(state=state.value)
