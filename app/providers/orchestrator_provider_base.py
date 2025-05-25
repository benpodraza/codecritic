from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider
from app.db.schemas import StateTransitionLogSchema
from app.enums.logging_enums import LogType

class OrchestratorProviderBase(BaseProvider):
    """Base class for orchestrator providers built on system FSMs."""

    def _run_provider(self, input: dict) -> str:
        return self._run(input)

    def transition(self, state: dict, session_id: str) -> dict:
        from_state = state.get("state")
        new_state = self._transition(state)
        to_state = new_state.get("state")

        self.logger.write(LogType.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=session_id,
            entity_type=self.__class__.__name__,
            entity_id=self.config.id,
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(timezone.utc)
        ))

        return new_state

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError

    @abstractmethod
    def _transition(self, state: dict) -> dict:
        raise NotImplementedError