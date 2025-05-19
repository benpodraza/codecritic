from typing import Any, Callable

from app.abstract_classes.state_manager_base import StateManagerBase

from app.enums.system_enums import SystemState
from app.extensions.agents.dummy_agent import DummyAgent


class DummyStateManager(StateManagerBase):
    """Concrete StateManager implementation leveraging scoring and context."""

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
            agent=agent,
            logger=logger,
        )
        self.current_state = SystemState.START

    def _run_state_logic(self, *args, **kwargs) -> None:
        self._log.info(f"Executing logic for state: {self.current_state.name}")
        self.agent.run(action=self.current_state.name)

    def _transition_state(self, from_state: str, to_state: str, reason: str) -> None:
        self._log.info(
            f"Dummy transition from {from_state} to {to_state} for reason: {reason}"
        )
        self.agent.run(action=to_state)
