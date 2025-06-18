from __future__ import annotations
from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict

from app.enums.fsm_enums import DECISION_TYPE, STATE_TYPE
from app.enums.logging_enums import RunContext
from app.enums.system_enums import SYSTEM
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import ControllerOutputSchema
from app.utilities.extract_base_filename import extract_base_filename
from app.utilities.select_best_file_by_score import select_best_file_by_score


class ControllerProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        system_providers=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self._systems = system_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []
        self._generated_files = []

    def _run_provider(self, input: dict) -> ControllerOutputSchema:
        session_id = input.get("session_id")

        incoming_file = input.get("file_path") or input.get("file_name") or input.get("before")
        if not incoming_file:
            raise ValueError("❌ ControllerProvider requires 'file_path', 'file_name', or 'before' in input")

        self.incoming_file = incoming_file
        src = Path(incoming_file).resolve()
        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        working_dir = Path("working_files").resolve()
        working_dir.mkdir(parents=True, exist_ok=True)
        root = extract_base_filename(src)
        self.working_file = working_dir / f"{root}__ctrl_{timestamp}{src.suffix}"
        shutil.copy(src, self.working_file)
        self._generated_files.append(self.working_file)

        input_path = Path(incoming_file)
        try:
            relative_path = str(input_path.relative_to(Path.cwd()))
        except ValueError:
            relative_path = str(input_path)

        state = {
            "state": SYSTEM.START,
            "file_path": str(self.working_file),
            "session_id": session_id,
            "reason": input.get("reason", SYSTEM.START.value),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state", SYSTEM.START),
            "decision": DECISION_TYPE.UNKNOWN,
            "original_file": relative_path,
            "run_id": self._run_id,
        }

        step_count = 0

        while True:
            current = state.get("state")

            if step_count >= self._max_steps:
                transition = self.transition(state, output)
                state.update({
                    **transition,
                    "state": SYSTEM.END,
                    "state_type": STATE_TYPE.END,
                    "reason": f"Max steps ({self._max_steps}) reached"
                })
                return ControllerOutputSchema(
                    state=SYSTEM.END,
                    previous_state=current,
                    state_type=SYSTEM.END,
                    decision=DECISION_TYPE.REJECTED,
                    steps=state.get("steps", step_count),
                    max_steps=self._max_steps,
                    summary=f"Max steps ({self._max_steps}) reached",
                    output=state,
                    provider_name=self._config.name,
                )

            if current == SYSTEM.END:
                best_file = select_best_file_by_score(
                    file_a=state["file_path"],
                    file_b=self.incoming_file,
                    score_provider=self.score_provider,
                    context=self._context
                )

                temp_path = Path("working_files") / f"temp_ctrl_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
                shutil.copy(Path(best_file), temp_path)
                state["file_path"] = str(temp_path)

                for f in Path("working_files").glob("temp_ctrl_*.py"):
                    if f.resolve() != temp_path.resolve():
                        try:
                            f.unlink()
                        except Exception:
                            pass

                for f in Path("working_files").glob("*_stripped.py"):
                    try:
                        f.unlink()
                    except Exception:
                        pass

                for path in self._generated_files:
                    if path.exists():
                        try:
                            path.unlink()
                        except Exception:
                            pass

                return ControllerOutputSchema(
                    state=SYSTEM.END,
                    previous_state=state.get("_last_state", SYSTEM.START),
                    state_type=STATE_TYPE.END,
                    decision=state.get("decision", DECISION_TYPE.UNKNOWN),
                    steps=state.get("steps", step_count),
                    max_steps=self._max_steps,
                    summary=state.get("summary", "Completed"),
                    output=state,
                    provider_name=self._config.name,
                )

            step_count += 1

            if current == SYSTEM.START:
                transition = self.transition(state, None)
                state.update(transition)
                state["_last_state"] = SYSTEM.START
                continue

            provider = self._systems.get(current.value)
            if not provider:
                raise ValueError(f"No system provider registered for state: {current.value}")

            provider_input = {k: v for k, v in state.items() if k != "state"}
            output = provider.run(input=provider_input, context=self.fork_context())

            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)
            promoted_path = Path("working_files") / f"temp_ctrl_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
            if "file_path" in output.output:
                final_path = Path(output.output["file_path"]).resolve()
                shutil.copy(final_path, promoted_path)
                self._generated_files.append(promoted_path)
                state["file_path"] = str(promoted_path)

            if hasattr(output, "decision") and output.decision is not None:
                state["decision"] = output.decision

            transition_result = self.transition(state, output)
            transition_result.pop("file_path", None)

            transition_metadata = transition_result.get("transition_metadata", {}) or {}
            transition_metadata.update({
                "agent_output": flat_output.get("output", {}),
                "file_path": flat_output.get("file_path"),
            })
            transition_result["transition_metadata"] = transition_metadata

            raw_state = transition_result.get("state", current)
            state_enum = raw_state if isinstance(raw_state, SYSTEM) else SYSTEM(raw_state)

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
