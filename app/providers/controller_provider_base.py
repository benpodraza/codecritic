from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
from pathlib import Path
import shutil, json

from app.enums.system_enums import STATE_DECISION_TYPE
from app.providers.base_provider import BaseProvider
from app.factories.system_provider_factory import SystemProviderFactory
from app.db.schemas import ControllerOutputSchema, StateTransitionLogSchema
from app.enums.fsm_enums import STATE_TYPE, REASON_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.logging_enums import LOG_TYPE, PROVIDER_TYPE


class ControllerProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        engine=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
    ):
        super().__init__(config=config, engine=engine)
        self.context_provider = context_provider
        self.score_provider   = score_provider
        self.tool_providers   = tool_providers or []

        # instantiate sub-systems
        self._systems: Dict[str, object] = {}
        for name, sys_id in (config.config or {}).get("systems", {}).items():
            self._systems[name] = SystemProviderFactory.create(sys_id)

    def _run_provider(self, input: dict) -> ControllerOutputSchema:
        session_id = input.get("session_id")
        src = Path(input["file_name"])
        max_steps = input.get("max_steps", 20)

        self.working_file = src.with_name(f"{src.stem}_working{src.suffix}")
        shutil.copy(src, self.working_file)

        state = {
            "state": "start",
            "file_path": str(src),
            "working_file": str(self.working_file),
            **input,
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
                    provider_name=self.config.name
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
                    provider_name=self.config.name
                )

            step_count += 1

            if current == "start":
                nxt = self.transition(state, None)
                state.update(nxt, _last_state="start")
                continue

            sysprov = self._systems.get(current)
            if not sysprov:
                raise ValueError(f"No system registered for state '{current}'")

            inp = {k: v for k, v in state.items() if k != "state"}
            out = sysprov.run(input=inp, session_id=session_id)

            nxt = self.transition(state, out)
            flat_output = out.model_dump(exclude={"output"}) if hasattr(out, "model_dump") else dict(out)
            state.update(nxt, _last_state=current, output=flat_output)


    def transition(self, state: dict, sys_output: dict | None) -> dict:
        next_state = self._transition(state, sys_output)
        state["steps"] = state.get("steps", 0) + 1

        self.logger.write(LOG_TYPE.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=state.get("session_id"),
            entity_type=PROVIDER_TYPE.CONTROLLER,
            entity_id=self.config.id,
            from_state=state.get("state"),
            to_state=next_state.get("state", "unknown"),
            reason=next_state.get("reason", TRANSITION_REASON_TYPE.CUSTOM_RULE),
            decision = STATE_DECISION_TYPE.REJECT if "accept" not in str(sys_output) else STATE_DECISION_TYPE.IMPROVED,
            triggered_by=self.config.name,
            step=state["steps"],
            transition_metadata={k: v for k, v in next_state.items() if k not in {"state", "reason", "decision"}},
            timestamp=datetime.now(timezone.utc)
        ))
        return next_state


    @abstractmethod
    def _transition(self, state: dict, sys_output: dict | None) -> dict:
        """Return next state dict: {'state': '...', 'reason': '...'}. Do not return an output schema."""
        ...
