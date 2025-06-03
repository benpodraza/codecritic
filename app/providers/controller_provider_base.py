from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
from pathlib import Path
import shutil, json

from app.enums.system_enums import STATE_DECISION_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import ControllerOutputSchema
from app.enums.fsm_enums import STATE_TYPE, REASON_TYPE


class ControllerProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        system_providers: Dict[str, object] = None,
        called_by_type=None,
        called_by_id=None,
    ):
        super().__init__(
            config=config,
            called_by_type=called_by_type,
            called_by_id=called_by_id
        )
        self.context_provider = context_provider
        self.score_provider   = score_provider
        self.tool_providers   = tool_providers or []
        self._states = system_providers or {}

    def _run_provider(self, input: dict) -> ControllerOutputSchema:
        session_id = input.get("session_id")
        src = Path(input["file_name"])
        max_steps = input.get("max_steps", 20)

        self.working_file = src.with_name(f"{src.stem}_working{src.suffix}")
        shutil.copy(src, self.working_file)

        state = {
            "state": "start",
            "file_name": input["file_name"],
            "working_file": str(self.working_file),
            "session_id": session_id,
            "system": input.get("system", "unknown"),
            "reason": input.get("reason", "start"),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
        }

        step_count = 0

        while True:
            current = state["state"]

            if step_count >= max_steps:
                return ControllerOutputSchema(
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
                return ControllerOutputSchema(
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
                nxt = self.transition(state, None)
                state.update(nxt, _last_state="start")
                continue

            provider = self._states.get(current)
            if not provider:
                raise ValueError(f"No system provider registered for state '{current}'")

            inp = {k: v for k, v in state.items() if k != "state"}
            out = provider.run(input=inp, session_id=session_id)

            nxt = self.transition(state, out)
            flat_output = out.model_dump(exclude={"output"}) if hasattr(out, "model_dump") else dict(out)
            clean_nxt = {k: v for k, v in nxt.items() if k != "output"}

            # Flatten controller's state output
            state.update(clean_nxt, _last_state=current)
            state["output"] = flat_output.get("output", {})  # only keep what's in `.output`


    @abstractmethod
    def _transition(self, state: dict, sys_output: dict | None) -> dict:
        """Return next state dict: {'state': '...', 'reason': '...'}. Do not return an output schema."""
        ...
