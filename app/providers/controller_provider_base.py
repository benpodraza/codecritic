from __future__ import annotations
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict

from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import ControllerOutputSchema

class ControllerProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        system_providers: Dict[str, object] = None,
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
        self._systems = system_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> ControllerOutputSchema:
        session_id = input.get("session_id")
        max_steps = input.get("max_steps", 20)

        incoming_file = input.get("file_path") or input.get("file_name") or input.get("before")

        if not incoming_file:
            raise ValueError("❌ ControllerProvider requires 'file_path', 'file_name', or 'before' in input")

        self.incoming_file = incoming_file

        src = Path(incoming_file).resolve()
        # derive base name without any suffixes or appended labels
        root = src.stem.split('.')[0]
        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        working_dir = Path("working_files").resolve()
        working_dir.mkdir(parents=True, exist_ok=True)
        self.working_file = working_dir / f"{root}.__ctrl_{timestamp}{src.suffix}"
        shutil.copy(src, self.working_file)

        state = {
            "state": "start",
            "file_path": str(self.working_file),
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
                return ControllerOutputSchema(
                    state="end",
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    decision=DECISION_TYPE.UNKNOWN,
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
                    decision=state.get("decision", DECISION_TYPE.UNKNOWN),
                    steps=step_count,
                    max_steps=max_steps,
                    summary=state.get("summary", "Completed"),
                    output=state,
                    provider_name=self._config.name
                )

            step_count += 1

            if current == "start":
                transition = self.transition(state, None)
                state.update(transition, _last_state="start")
                continue

            provider = self._systems.get(current)
            if not provider:
                raise ValueError(f"No system provider registered for state: {current}")

            provider_input = {k: v for k, v in state.items() if k != "state"}
            output = provider.run(input=provider_input, session_id=session_id)

            transition_result = self.transition(state, output)
            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)

            # if the provider accepted, update the working copy
            if getattr(output, "decision", None) == DECISION_TYPE.ACCEPT:
                new_path = getattr(output, "file_path", None) or provider_input.get("file_path")
                if new_path:
                    new_path = Path(new_path).resolve()
                    current_path = Path(state["file_path"]).resolve()
                    if new_path != current_path and new_path.exists():
                        shutil.copy(new_path, current_path)

            state = {
                **state,
                **transition_result,
                "file_path": transition_result.get("file_path") or getattr(output, "file_path", state.get("file_path")),
                "score": getattr(output, "score", None),
                "_last_state": current,
                "state_output": flat_output,
            }

    @abstractmethod
    def _transition(self, state: dict, output: dict | None) -> dict:
        ...