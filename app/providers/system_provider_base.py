from __future__ import annotations
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict
from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import SystemOutputSchema


class SystemProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        state_providers: Dict[str, object] = None,
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
        self._states = state_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> SystemOutputSchema:
        session_id = input.get("session_id")
        max_steps = input.get("max_steps", 10)

        incoming_file = input.get("file_path") or input.get("file_name") or input.get("before")

        if not incoming_file:
            raise ValueError("❌ StateProvider requires 'file_path', 'file_name', or 'before' in input")

        self.incoming_file = incoming_file

        src = Path(incoming_file).resolve()
        timestamp = datetime.now().strftime('%H%M%S%f')[:10]
        working_dir = Path("working_files").resolve()
        working_dir.mkdir(parents=True, exist_ok=True)
        # Extract base name before any suffix (e.g., strip "__ctrl_...", "__prog_...", etc.)
        root = src.name.partition('.')[0]
        self.working_file = working_dir / f"{root}.__sys_{timestamp}{src.suffix}"
        shutil.copy(src, self.working_file)

        state = {
            "state": "start",
            "file_path": str(self.working_file),
            "session_id": input.get("session_id"),
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
                return SystemOutputSchema(
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
                return SystemOutputSchema(
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

            provider = self._states.get(current)
            if not provider:
                raise ValueError(f"No state provider registered for state: {current}")

            provider_input = {k: v for k, v in state.items() if k != "state"}
            output = provider.run(input=provider_input, session_id=session_id)

            # --- Update working file if provider returned a new file_path
            new_file_path = getattr(output, "file_path", None)
            if new_file_path and new_file_path != state.get("file_path"):
                # Replace current working file with the new one
                shutil.copy(Path(new_file_path).resolve(), Path(state.get("file_path")))

            transition_result = self.transition(state, output)
            flat_output = output.model_dump(exclude={"output"}) if hasattr(output, "model_dump") else dict(output)

            state = {
                **state,
                **transition_result,
                "file_path": transition_result.get("file_path") or getattr(output, "file_path", state.get("file_path")),
                "score": getattr(output, "score", None),
                "_last_state": current,
                "state_output": flat_output,
            }
