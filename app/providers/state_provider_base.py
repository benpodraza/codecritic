from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
import json

from app.enums.system_enums import STATE_DECISION_TYPE
from app.providers.base_provider import BaseProvider
from app.db.schemas import StateTransitionLogSchema, StateOutputSchema
from app.enums.fsm_enums import STATE_TYPE, REASON_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.logging_enums import LOG_TYPE, PROVIDER_TYPE


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

    def _run_provider(self, input: dict) -> StateOutputSchema:
        session_id = input.get("session_id")
        state = {"state": "start", **input}
        step_count = 0
        max_steps = input.get("max_steps", 20)

        while True:
            current = state.get("state")

            if step_count >= max_steps:
                return StateOutputSchema(
                    state="end",
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    reason=REASON_TYPE.MAX_STEPS,
                    decision=STATE_DECISION_TYPE.UNKNOWN,
                    steps=step_count,
                    max_steps=max_steps,
                    summary="Max steps reached",
                    output=state,
                    provider_name=self.config.name
                )

            if current == "end":
                return StateOutputSchema(
                    state="end",
                    previous_state=state.get("_last_state"),
                    state_type=STATE_TYPE.END,
                    reason=REASON_TYPE.SUCCESS,
                    decision=STATE_DECISION_TYPE.FINAL,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=state.get("reason", "Completed"),
                    output=state,
                    provider_name=self.config.name
                )

            step_count += 1

            if current == "start":
                transition = self.transition(state, None)
                state.update(transition)
                state["_last_state"] = "start"
                continue

            agent = self._agents.get(current)
            if not agent:
                raise ValueError(f"No agent registered for state: {current}")

            agent_output = agent.run(input=state, session_id=session_id)
            transition = self.transition(state, agent_output)
            state.update({
                **transition,
                "_last_state": current,
                "agent_output": agent_output,
                "output": agent_output
            })


    def transition(self, state: dict, agent_output: str | None) -> dict:
        next_state = self._transition(state, agent_output)
        state["steps"] = state.get("steps", 0) + 1

        self.logger.write(LOG_TYPE.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=state.get("session_id"),
            entity_type=PROVIDER_TYPE.STATE,
            entity_id=self.config.id,
            from_state=state.get("state"),
            to_state=next_state.get("state", "unknown"),
            reason=next_state.get("reason", TRANSITION_REASON_TYPE.CUSTOM_RULE),
            decision = STATE_DECISION_TYPE.REJECT if "accept" not in str(agent_output) else STATE_DECISION_TYPE.IMPROVED,
            triggered_by=self.config.name,
            step=state["steps"],
            transition_metadata={k: v for k, v in next_state.items() if k not in {"state", "reason", "decision"}},
            timestamp=datetime.now(timezone.utc)
        ))
        return next_state

    @abstractmethod
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        raise NotImplementedError
