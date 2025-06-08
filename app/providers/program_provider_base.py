from __future__ import annotations
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict

from app.enums.controller_enums import CONTROLLER
from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import ProgramOutputSchema
from app.utilities.extract_base_filename import extract_base_filename
from app.utilities.select_best_file_by_score import select_best_file_by_score


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
        self._generated_files: list[Path] = []

    def _run_provider(self, input: dict) -> ProgramOutputSchema:
        session_id = input.get("session_id")
        max_steps = input.get("max_steps", 20)

        incoming_file = input.get("file_path")
        self.incoming_file = incoming_file

        # Optional output path from input dictionary
        output_path = input.get("output_path", "working_files")

        src = Path(incoming_file).resolve()
        root = extract_base_filename(src)
        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        working_dir = Path("working_files").resolve()
        working_dir.mkdir(parents=True, exist_ok=True)
        self.working_file = working_dir / f"{root}.__prog_{timestamp}{src.suffix}"
        shutil.copy(src, self.working_file)
        self._generated_files.append(self.working_file)

        input_path = Path(incoming_file)
        try:
            relative_path = str(input_path.relative_to(Path.cwd()))
        except ValueError:
            relative_path = str(input_path)

        state = {
            "state": CONTROLLER.START,
            "file_path": str(self.working_file),
            "session_id": session_id,
            "system": input.get("system", "unknown"),
            "reason": input.get("reason", CONTROLLER.START.value),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state", CONTROLLER.START),
            "original_file": relative_path,
            "run_id": self._run_id,
        }

        step_count = 0

        while True:
            current = state.get("state")

            if step_count >= max_steps:
                return ProgramOutputSchema(
                    state=CONTROLLER.END,
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    decision=DECISION_TYPE.UNKNOWN,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=f"Max steps ({max_steps}) reached",
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
                    file_b=self.incoming_file,
                    score_provider=self.score_provider,
                    system=state.get("system", "unknown"),
                    session_id=session_id
                )

                # If an output_path is provided, use that path, otherwise default to working_files
                final_path = Path(output_path) / Path(self.incoming_file).name
  
                shutil.copy(Path(best_file).resolve(), final_path)
                state["file_path"] = str(final_path)
                state["decision"] = final_decision

                # Delete old files in working directory
                for f in Path("working_files").glob("temp_*.py"):
                    if f.resolve() != final_path.resolve():
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

                return ProgramOutputSchema(
                    state=CONTROLLER.END,
                    previous_state=state.get("_last_state", CONTROLLER.START),
                    state_type=STATE_TYPE.END,
                    decision=final_decision or DECISION_TYPE.UNKNOWN,
                    steps=step_count,
                    max_steps=max_steps,
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
            output = provider.run(input=provider_input, session_id=session_id)

            transition_result = self.transition(state, output)
            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)

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
                "file_path": transition_result.get("file_path") or getattr(output, "file_path", state.get("file_path")),
                "_last_state": current,
                "state_output": flat_output,
            }

    @abstractmethod
    def _transition(self, state: dict, output: dict | None) -> dict:
        ...
