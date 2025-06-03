from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from app.enums.system_enums import STATE_DECISION_TYPE
from app.enums.fsm_enums import STATE_TYPE, REASON_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import ProgramOutputSchema


class ProgramProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        controller_providers: Dict[str, object] = None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        called_by_type=None,
        called_by_id=None,
    ):
        super().__init__(
            config=config,
            called_by_type=called_by_type,
            called_by_id=called_by_id
        )
        self._states = controller_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> ProgramOutputSchema:
        session_id = input.get("session_id")
        max_steps = input.get("max_steps", 20)

        state = {
            "state": "start",
            "file_name": input.get("file_name"),
            "working_file": input.get("working_file"),
            "session_id": session_id,
            "system": input.get("system", "unknown"),
            "reason": input.get("reason", "start"),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state"),
        }

        step_count = 0

        while True:
            current = state.get("state")

            if step_count >= max_steps:
                return ProgramOutputSchema(
                    state="end",
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    reason=REASON_TYPE.MAX_STEPS,
                    decision=STATE_DECISION_TYPE.UNKNOWN,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=f"Max steps ({max_steps}) reached",
                    output=state,
                    provider_name=self._config.name
                )

            if current == "end":
                return ProgramOutputSchema(
                    state="end",
                    previous_state=state.get("_last_state"),
                    state_type=STATE_TYPE.END,
                    reason=REASON_TYPE.SUCCESS,
                    decision=STATE_DECISION_TYPE.FINAL,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=state.get("reason", "Completed"),
                    output=state,
                    provider_name=self._config.name
                )

            step_count += 1

            if current == "start":
                transition = self.transition(state, None)
                state.update(transition, _last_state="start")
                continue

            provider = self._states.get(current)
            if not provider:
                raise ValueError(f"No controller provider registered for state: {current}")

            provider_input = {k: v for k, v in state.items() if k != "state"}
            output = provider.run(input=provider_input, session_id=session_id)

            transition_result = self.transition(state, output)
            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)

            state = {
                **state,
                **transition_result,
                "_last_state": current,
                "output": flat_output.get("output", {})
            }

    @abstractmethod
    def _transition(self, state: dict, output: dict | None) -> dict:
        ...