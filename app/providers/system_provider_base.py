from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Dict

from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.logging_enums import RunContext
from app.enums.state_enums import STATE
from app.enums.system_enums import SYSTEM
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import SystemOutputSchema
from app.utilities.extract_base_filename import extract_base_filename
from app.utilities.select_best_file_by_score import select_best_file_by_score
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()


class SystemProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        state_providers=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self._states = state_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []
        self._generated_files: list[str] = []

    def _run_provider(self, input: dict) -> SystemOutputSchema:
        session_id = input.get("session_id")

        incoming_file = input.get("file_path")
        if not incoming_file:
            raise ValueError("❌ SystemProvider requires 'file_path' in input")

        self.incoming_file = incoming_file
        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        root = extract_base_filename(incoming_file)
        working_filename = f"{root}__sys_{timestamp}.py"
        self.working_file = working_filename
        fm.copy(FILETYPE.WORKING, incoming_file, FILETYPE.WORKING, dst_filename=working_filename)
        self._generated_files.append(working_filename)

        state = {
            "state": STATE.START,
            "file_path": working_filename,
            "session_id": session_id,
            "reason": input.get("reason", STATE.START.value),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state", STATE.START),
            "decision": DECISION_TYPE.UNKNOWN,
            "original_file": incoming_file,
            "run_id": self._run_id,
        }

        step_count = 0

        while True:
            current = state["state"]

            if step_count >= self._max_steps:
                transition = self.transition(state, output)
                state.update({
                    **transition,
                    "state": STATE.END,
                    "state_type": STATE_TYPE.END,
                    "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL
                })
                return SystemOutputSchema(
                    state=STATE.END,
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    decision=DECISION_TYPE.REJECTED,
                    steps=state.get("steps", step_count),
                    max_steps=self._max_steps,
                    summary=f"Max steps ({self._max_steps}) reached",
                    output=state,
                    provider_name=self._config.name
                )

            if current == STATE.END:
                transition = self.transition(state, output)
                state.update(transition)

                best_file = select_best_file_by_score(
                    file_a=state["file_path"],
                    file_b=self.incoming_file,
                    score_provider=self.score_provider,
                    context=self._context
                )

                temp_name = f"temp_sys_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
                fm.copy(FILETYPE.WORKING, best_file, FILETYPE.WORKING, dst_filename=temp_name)
                state["file_path"] = temp_name

                for f in fm.list_files(FILETYPE.WORKING):
                    if f.startswith("temp_sys_") and f != temp_name:
                        fm.delete(FILETYPE.WORKING, f)
                    elif f.endswith("_stripped.py"):
                        fm.delete(FILETYPE.WORKING, f)

                for path in self._generated_files:
                    fm.delete(FILETYPE.WORKING, path)

                return SystemOutputSchema(
                    state=STATE.END,
                    previous_state=state.get("_last_state", STATE.START),
                    state_type=STATE_TYPE.END,
                    decision=state.get("decision", DECISION_TYPE.UNKNOWN),
                    steps=state.get("steps", step_count),
                    max_steps=self._max_steps,
                    summary=state.get("summary", "Completed"),
                    output=state,
                    provider_name=self._config.name
                )

            step_count += 1

            if current == STATE.START:
                transition = self.transition(state, None)
                state.update(transition)
                state["_last_state"] = STATE.START
                continue

            provider = self._states.get(current.value)
            if not provider:
                raise ValueError(f"No state provider registered for state: {current.value}")

            provider_input = {k: v for k, v in state.items() if k != "state"}
            output = provider.run(input=provider_input, context=self.fork_context())

            new_file_path = output.output.get("file_path")
            if new_file_path:
                state["file_path"] = str(new_file_path)

            if hasattr(output, "decision") and output.decision:
                state["decision"] = output.decision

            transition_result = self.transition(state, output)
            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)

            transition_metadata = transition_result.get("transition_metadata", {}) or {}
            transition_metadata.update({
                "agent_output": flat_output.get("output", {}),
                "file_path": flat_output.get("file_path"),
            })
            transition_result["transition_metadata"] = transition_metadata
            transition_result.pop("file_path", None)

            raw_state = transition_result.get("state", current)
            state_enum = raw_state if isinstance(raw_state, STATE) else STATE(raw_state)

            state = {
                **state,
                **transition_result,
                "state": state_enum,
                "_last_state": current,
                "state_output": flat_output,
            }

    @abstractmethod
    def _transition(self, state: dict, output: dict | None) -> dict:
        ...
