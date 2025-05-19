from datetime import datetime, timezone
from typing import Any, Callable
from enum import Enum

from ...abstract_classes.state_manager_base import StateManagerBase
from ...enums.logging_enums import LogType
from ...enums.system_enums import SystemState
from ...extensions.agents.dummy_agent import DummyAgent


class DummyStateManager(StateManagerBase):
    """Example concrete StateManager leveraging scoring and context."""

    def __init__(
        self,
        scoring_function: Callable[[Any], float],
        context_manager: Any,
        agent: DummyAgent,
        logger=None,
    ) -> None:
        super().__init__(
            scoring_function=scoring_function,
            context_manager=context_manager,
            logger=logger,
        )
        self.agent = agent
        self.current_state = SystemState.START

    def _run_state_logic(self, *args, **kwargs) -> None:
        self._log.info("Dummy state logic executed")

    def transition_state(
        self,
        experiment_id: str,
        round: int,
        from_state: Enum,
        to_state: Enum,
        reason: str,
    ) -> None:
        """Validate transition, log it, and invoke the next state's agent."""

        context = {}
        if self.context_manager is not None:
            context = self.context_manager.get_context(
                experiment_id=experiment_id, round=round
            )

        score = 0.0
        if self.scoring_function is not None:
            score = self.scoring_function(context)
        if score < 0:
            raise ValueError("Invalid transition score")

        self.logger.write(
            LogType.STATE_TRANSITION,
            {
                "experiment_id": experiment_id,
                "round": round,
                "from_state": from_state.name,
                "to_state": to_state.name,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.current_state = SystemState(to_state.value)
        self.agent.run(experiment_id=experiment_id, round=round, action=to_state.name)
