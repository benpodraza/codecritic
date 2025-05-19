from typing import Optional, List
from datetime import datetime, timezone
from app.abstract_classes.agent_base import AgentBase
from app.utilities.metadata.logging.log_schemas import (
    StateTransitionLog,
    StateLog,
)
from app.factories.logging_provider import LoggingProvider, LogType
from app.enums.system_enums import StateTransitionReason, SystemState


class StateManager(StateManagerBase):
    def __init__(
        self,
        scoring_function,
        context_manager,
        agent: Optional[AgentBase] = None,
        logger: LoggingProvider | None = None,
    ) -> None:
        super().__init__(
            scoring_function=scoring_function,
            context_manager=context_manager,
            agent=agent,
            logger=logger,
        )
        self.current_state = SystemState.START
        self.state_logs: List[StateLog] = []
        self.transition_logs: List[StateTransitionLog] = []

    def _run_state_logic(self, *args, **kwargs) -> None:
        state = kwargs.get("state")
        self._log.info("Running state logic for state: %s", state)

    def _transition_state(self, from_state: str, to_state: str, reason: str) -> None:
        self._log.info(
            "Transitioning from %s to %s due to reason: %s",
            from_state,
            to_state,
            reason,
        )
        self.current_state = SystemState(to_state)

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
