from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timezone
from typing import Optional

from app.enums.fsm_enums import TRANSITION_REASON_TYPE, DECISION_TYPE
from app.enums.logging_enums import LOG_TYPE, PROVIDER_TYPE, RunContext
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
        context: RunContext = None,
        **kwargs
    ) -> None:
        super().__init__(
            config=config,
            context=context,
            **kwargs
        )

    def transition(self, state: dict, result: dict | None) -> dict:
        next_state = self._transition(state, result)

        required_keys = {"state", "reason"}
        missing_keys = required_keys - next_state.keys()
        if missing_keys:
            raise ValueError(f"❌ Transition result missing keys: {missing_keys}\nReturned: {next_state}")
        state["steps"] = state.get("steps", 0) + 1

        # Ensure original_file is carried forward
        original_file = state.get("original_file")

        # Initialize or update transition_metadata
        transition_metadata = next_state.get("transition_metadata", {}) or {}
        transition_metadata["original_file"] = original_file

        # Optional: Add run_id to the metadata as well
        transition_metadata["run_id"] = state.get("run_id")

        # Optional: agent_output propagation (if result has a dumpable output)
        if isinstance(result, dict):
            transition_metadata["agent_output"] = result.get("output")
            transition_metadata["file_path"] = result.get("file_path")

        next_state["transition_metadata"] = transition_metadata

        is_terminal = next_state.get("state_type") == "end" or next_state.get("state") == "end"

        decision = getattr(result, "decision", DECISION_TYPE.UNKNOWN)
        # Log the state transition with relevant details
        self.logger.write(
            LOG_TYPE.STATE_TRANSITION,
            StateTransitionLogSchema(
                session_id=self._session_id,
                file_log_id=self._file_log_id, 
                entity_type=self._infer_provider_type(),
                entity_id=self._config.id,
                from_state=state.get("state"),
                to_state=next_state.get("state", "unknown"),
                reason=TRANSITION_REASON_TYPE(next_state["reason"]),
                decision=decision,
                triggered_by=self._config.name,
                step=state["steps"],
                transition_metadata=transition_metadata,
                timestamp=datetime.now(timezone.utc),
                run_id=self._run_id,
                called_by_type=self._called_by_type if self._called_by_type else None,
                called_by_id=self._called_by_id,
                parent_id=self._context.parent_id if self._context else None,
                execution_chain=self._context.execution_chain[:] if self._context else [],
            ),
        )
        return next_state


    @abstractmethod
    def _transition(self, state: dict, result: dict | None) -> dict:
        raise NotImplementedError
