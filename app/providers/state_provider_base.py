from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
import json

from app.providers.base_provider import BaseProvider
from app.db.schemas import StateTransitionLogSchema, ProviderLogSchema
from app.enums.logging_enums import LogType


class StateProviderBase(BaseProvider):
    """Base class for FSM-driven state providers."""

    def __init__(
        self,
        config=None,
        engine=None,
        agents: dict[str, object] = None,
        context_provider=None,
        score_provider=None,
        tool_providers=None
    ):
        super().__init__(config=config, engine=engine)
        self._agents = agents or {}
        self._context_provider = context_provider
        self._score_provider = score_provider
        self._tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> dict:
        session_id = input.get("session_id")
        state = {"state": "start", **input}

        while True:
            current = state.get("state")

            if current == "end":
                self.logger.write(LogType.PROVIDER, ProviderLogSchema(
                    session_id=session_id,
                    provider_id=self.config.id,
                    provider_type=self.__class__.__name__,
                    input=json.dumps(input),
                    output=json.dumps(state),
                    file_path=self.config.artifact_path,
                    timestamp=datetime.now(timezone.utc)
                ))
                return state

            if current == "start":
                state = {**state, **self.transition(state, None), "_last_state": "start"}
                continue

            agent = self._agents.get(current)
            if not agent:
                raise ValueError(f"No agent registered for state: {current}")

            output = agent.run(input=state, session_id=session_id)
            state = {**state, **self.transition(state, output), "_last_state": current, "output": output}

    def transition(self, state: dict, agent_output: str | None) -> dict:
        next_state = self._transition(state, agent_output)
        self.logger.write(LogType.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=state.get("session_id"),
            entity_type=self.__class__.__name__,
            entity_id=self.config.id,
            from_state=state.get("state"),
            to_state=next_state.get("state", "unknown"),
            reason=next_state.get("reason", "unspecified"),
            timestamp=datetime.now(timezone.utc)
        ))
        return next_state

    @abstractmethod
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        raise NotImplementedError
