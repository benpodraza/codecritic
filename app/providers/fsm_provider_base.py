from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timezone
from typing import Optional

from app.enums.fsm_enums import TRANSITION_REASON_TYPE
from app.enums.logging_enums import LOG_TYPE, PROVIDER_TYPE
from app.enums.system_enums import STATE_DECISION_TYPE
from app.db.schemas import StateTransitionLogSchema
from app.providers.base_provider import BaseProvider


class FSMProviderBase(BaseProvider):
    """
    Base class for FSM-enabled providers (Program, Controller, System, State).
    Provides a shared `transition` method and logging of state transitions.
    """

    def __init__(
        self,
        config=None,
        called_by_type: Optional[PROVIDER_TYPE] = None,
        called_by_id: Optional[int] = None,
    ) -> None:
        super().__init__(
            config=config,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
        )

    def transition(self, state: dict, result: dict | None) -> dict:
        next_state = self._transition(state, result)
        state["steps"] = state.get("steps", 0) + 1

        self.logger.write(
            LOG_TYPE.STATE_TRANSITION,
            StateTransitionLogSchema(
                session_id=state.get("session_id"),
                entity_type=self._infer_provider_type(),
                entity_id=self._config.id,
                from_state=state.get("state"),
                to_state=next_state.get("state", "unknown"),
                reason=next_state.get("reason", TRANSITION_REASON_TYPE.CUSTOM_RULE),
                decision=(
                    STATE_DECISION_TYPE.REJECT
                    if "accept" not in str(result)
                    else STATE_DECISION_TYPE.IMPROVED
                ),
                triggered_by=self._config.name,
                step=state["steps"],
                transition_metadata={
                    k: v for k, v in next_state.items() if k not in {"state", "reason", "decision"}
                },
                timestamp=datetime.now(timezone.utc),
            ),
        )
        return next_state

    @abstractmethod
    def _transition(self, state: dict, result: dict | None) -> dict:
        raise NotImplementedError
