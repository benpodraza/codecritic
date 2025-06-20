from __future__ import annotations

from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict

from app.enums.controller_enums import CONTROLLER
from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.enums.logging_enums import RunContext, LOG_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import ProgramOutputSchema, FileLogSchema
from app.utilities.extract_base_filename import extract_base_filename
from app.utilities.select_best_file_by_score import select_best_file_by_score
from app.utilities.metadata.logging.logging_provider import LoggingProvider
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()


class ProgramProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        controller_providers: Dict[str, object] = None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        context: RunContext = None,
    ):
        super().__init__(config=config, context=context)
        self._states = controller_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []
        self._session_id = context.session_id
        self._file_log_id = context.file_log_id
        self._generated_files: list[str] = []

    def _run_provider(self, input: dict) -> ProgramOutputSchema:
        session_id = self._session_id
        incoming_file = input.get("file_path")
        if not incoming_file:
            raise ValueError("ProgramProvider requires 'file_path' in input")

        self.incoming_file = incoming_file
        output_path = input.get("output_path", "working_files")

        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        root = extract_base_filename(incoming_file)
        working_filename = f"{root}.__prog_{timestamp}.py"
        self.working_file = working_filename
        fm.copy(FILETYPE.INPUT, incoming_file, FILETYPE.WORKING, dst_filename=working_filename)
        fm.copy(FILETYPE.INPUT, incoming_file, FILETYPE.WORKING, dst_filename=Path(incoming_file).name)
        self._generated_files.append(working_filename)

        file_log = FileLogSchema(
            session_id=session_id,
            file_name=Path(incoming_file).name,
            original_path=incoming_file,
            length_bytes=len(fm.load(FILETYPE.INPUT, incoming_file).encode("utf-8")),
        )
        self._file_log_id = LoggingProvider().write(LOG_TYPE.FILE, file_log)
        self._context.file_log_id = self._file_log_id
        self.context = self._context

        state = {
            "state": CONTROLLER.START,
            "file_path": working_filename,
            "session_id": session_id,
            "file_log_id": self._file_log_id,
            "reason": input.get("reason", CONTROLLER.START.value),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state", CONTROLLER.START),
            "decision": DECISION_TYPE.UNKNOWN,
            "original_file": incoming_file,
            "run_id": self._run_id,
        }

        step_count = 0

        while True:
            current = state.get("state")

            if step_count >= self._max_steps:
                transition = self.transition(state, output)
                state.update({
                    **transition,
                    "state": CONTROLLER.END,
                    "state_type": STATE_TYPE.END,
                    "reason": f"Max steps ({self._max_steps}) reached"
                })
                return ProgramOutputSchema(
                    state=CONTROLLER.END,
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    decision=DECISION_TYPE.UNKNOWN,
                    steps=state.get("steps", step_count),
                    max_steps=self._max_steps,
                    summary=f"Max steps ({self._max_steps}) reached",
                    output=state,
                    provider_name=self._config.name
                )

            if current == CONTROLLER.END:
                final_decision = state.get("decision")
                nested = state.get("output") or {}
                if isinstance(nested, dict):
                    final_decision = final_decision or nested.get("decision")

                best_file = select_best_file_by_score(
                    file_a=state.get("file_path"),
                    file_b=Path(self.incoming_file).name,
                    score_provider=self.score_provider,
                    context=self._context
                )

                final_name = Path(self.incoming_file).name
                fm.copy(FILETYPE.WORKING, best_file, FILETYPE.WORKING, dst_filename=final_name)
                state["file_path"] = final_name
                state["decision"] = final_decision

                for f in fm.list_files(FILETYPE.WORKING):
                    if f.startswith("temp_") and f != final_name:
                        fm.delete(FILETYPE.WORKING, f)
                    elif f.endswith("_stripped.py"):
                        fm.delete(FILETYPE.WORKING, f)

                for path in self._generated_files:
                    fm.delete(FILETYPE.WORKING, path)

                return ProgramOutputSchema(
                    state=CONTROLLER.END,
                    previous_state=state.get("_last_state", CONTROLLER.START),
                    state_type=STATE_TYPE.END,
                    decision=final_decision or state.get("decision", DECISION_TYPE.UNKNOWN),
                    steps=state.get("steps", step_count),
                    max_steps=self._max_steps,
                    summary=state.get("reason", "Completed"),
                    output=state,
                    provider_name=self._config.name
                )

            step_count += 1

            if current == CONTROLLER.START:
                transition = self.transition(state, None)
                state.update(transition)
                state["_last_state"] = CONTROLLER.START
                continue

            provider = self._states.get(current)
            if not provider:
                raise ValueError(f"No controller provider registered for state: {current}")

            provider_input = {k: v for k, v in state.items() if k != "state"}
            output = provider.run(input=provider_input, context=self.fork_context())

            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)
            if "file_path" in output.output:
                promoted_name = f"temp_prog_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
                fm.copy(FILETYPE.WORKING, output.output["file_path"], FILETYPE.WORKING, dst_filename=promoted_name)
                self._generated_files.append(promoted_name)
                state["file_path"] = promoted_name

            transition_result = self.transition(state, output)
            transition_result.pop("file_path", None)

            transition_metadata = transition_result.get("transition_metadata", {}) or {}
            transition_metadata.update({
                "agent_output": flat_output.get("output", {}),
                "file_path": flat_output.get("file_path"),
            })
            transition_result["transition_metadata"] = transition_metadata

            state = {
                **state,
                **transition_result,
                "state": CONTROLLER(transition_result.get("state", current)),
                "_last_state": current,
                "state_output": flat_output,
            }

    @abstractmethod
    def _transition(self, state: dict, output: dict | None) -> dict:
        ...
