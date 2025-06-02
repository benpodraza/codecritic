from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
from pathlib import Path
import shutil
import json

from app.enums.system_enums import STATE_DECISION_TYPE
from app.providers.base_provider import BaseProvider
from app.factories.state_provider_factory import StateProviderFactory
from app.db.schemas import StateTransitionLogSchema, SystemOutputSchema
from app.enums.fsm_enums import STATE_TYPE, REASON_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.logging_enums import LOG_TYPE, PROVIDER_TYPE


class SystemProviderBase(BaseProvider):
    def __init__(self, config=None, engine=None, context_provider=None, score_provider=None, tool_providers=None):
        super().__init__(config=config, engine=engine)
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []
        self._states: Dict[str, object] = {}
        state_cfg = config.config.get("states", {})

        for name, provider_id in state_cfg.items():
            self._states[name] = StateProviderFactory.create(provider_id)

    def _run_provider(self, input: dict) -> SystemOutputSchema:
        session_id = input.get("session_id")
        input_file = Path(input["file_path"])
        self.working_file = input_file.with_name(f"{input_file.stem}_working{input_file.suffix}")
        shutil.copy(input_file, self.working_file)

        state = {
            "state": "start",
            "input_file": str(input_file),
            "working_file": str(self.working_file),
            **input
        }

        max_steps = input.get("max_steps", 20)
        step_count = 0

        while True:
            if step_count >= max_steps:
                return SystemOutputSchema(
                    state="end",
                    previous_state=state.get("state"),
                    state_type=STATE_TYPE.END,
                    reason=REASON_TYPE.MAX_STEPS,
                    decision=STATE_DECISION_TYPE.UNKNOWN,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=f"Max steps ({max_steps}) reached",
                    output=state,
                    provider_name=self.config.name
                )

            step_count += 1
            current = state.get("state")

            if current == "end":
                return SystemOutputSchema(
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

            if current == "start":
                state = {**state, **self.transition(state, None), "_last_state": "start"}
                continue

            state_provider = self._states.get(current)
            if not state_provider:
                raise ValueError(f"No state provider registered for state: {current}")

            provider_input = {k: v for k, v in state.items() if k != "state"}

            output = state_provider.run(input=provider_input, session_id=session_id)

            transition_result = self.transition(state, output)

            state = {**state, **transition_result, "_last_state": current}
            if "output" not in output:
                state["output"] = output

    def transition(self, state: dict, agent_output: str | None) -> dict:
        next_state = self._transition(state, agent_output)
        state["steps"] = state.get("steps", 0) + 1

        self.logger.write(LOG_TYPE.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=state.get("session_id"),
            entity_type=PROVIDER_TYPE.SYSTEM,
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


    def update_working_file_from_snapshot(self, snapshot_path: str):
        after_file = Path(f"experiments/snapshots/{snapshot_path}.after")
        if after_file.exists():
            Path(self.working_file).write_text(after_file.read_text(encoding="utf-8"), encoding="utf-8")

    @abstractmethod
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        raise NotImplementedError
