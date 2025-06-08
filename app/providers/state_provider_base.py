from __future__ import annotations
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict

from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.enums.state_enums import STATE
from app.enums.agent_enums import AGENT
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import StateOutputSchema
from app.utilities.extract_base_filename import extract_base_filename
from app.utilities.select_best_file_by_score import select_best_file_by_score


class StateProviderBase(FSMProviderBase):
    def __init__(
        self,
        config=None,
        agent_providers: Dict[str, object] = None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        called_by_type=None,
        called_by_id=None,
    ):
        super().__init__(
            config=config,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
        )
        self.agent_providers = agent_providers or {}
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []
        self._generated_files: list[Path] = []

    def _run_provider(self, input: dict) -> StateOutputSchema:
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
        root = extract_base_filename(src)
        self.working_file = working_dir / f"{root}__state_{timestamp}{src.suffix}"
        shutil.copy(src, self.working_file)
        self._generated_files.append(self.working_file)

        input_path = Path(incoming_file)
        try:
            relative_path = str(input_path.relative_to(Path.cwd()))
        except ValueError:
            relative_path = str(input_path)

        state = {
            "state": AGENT.START,
            "file_path": str(self.working_file),
            "session_id": session_id,
            "system": input.get("system", "unknown"),
            "reason": input.get("reason", AGENT.START.value),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state", AGENT.START),
            "decision": DECISION_TYPE.UNKNOWN,
            "original_file": relative_path,
            "run_id": self._run_id,
        }

        step_count = 0

        while True:
            current = state["state"]

            if step_count >= max_steps:
                return StateOutputSchema(
                    state=AGENT.END,
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    decision=DECISION_TYPE.REJECTED,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=f"Max steps ({max_steps}) reached",
                    output=state,
                    provider_name=self._config.name,
                )

            if current == STATE.END:
                if self.score_provider:
                    best_file = select_best_file_by_score(
                        file_a=state["file_path"],
                        file_b=self.incoming_file,
                        score_provider=self.score_provider,
                        system=state.get("system", "unknown"),
                        session_id=session_id
                    )

                    temp_path = Path("working_files") / f"temp_state_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
                    shutil.copy(Path(best_file), temp_path)
                    state["file_path"] = str(temp_path)

                    for f in Path("working_files").glob("temp_state_*.py"):
                        if f.resolve() != temp_path.resolve():
                            try:
                                f.unlink()
                            except Exception:
                                pass
                    
                    for f in Path("working_files").glob("temp_agent_*.py"):
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

                return StateOutputSchema(
                    state=AGENT.END,
                    previous_state=state.get("_last_state", AGENT.START),
                    state_type=STATE_TYPE.END,
                    decision=state.get("decision", DECISION_TYPE.UNKNOWN),
                    steps=step_count,
                    max_steps=max_steps,
                    summary=state.get("summary", "Completed"),
                    output=state,
                    provider_name=self._config.name,
                )

            step_count += 1

            if current == AGENT.START:
                transition = self.transition(state, None)
                state.update(transition)
                state["_last_state"] = AGENT.START
                continue

            provider = self.agent_providers.get(current.value)
            agent_output = provider.run(input=state, session_id=session_id) if provider else None

            transition_result = self.transition(state, agent_output)

            new_file_path = transition_result.get("file_path") or getattr(agent_output, "file_path", None)
            if new_file_path:
                new_file_path = Path(new_file_path).resolve()
                current_path = Path(state["file_path"]).resolve()
                if new_file_path != current_path:
                    shutil.copy(new_file_path, current_path)
                    self._generated_files.append(new_file_path)
                    state["file_path"] = str(new_file_path)

            if hasattr(agent_output, "decision") and agent_output.decision:
                state["decision"] = agent_output.decision

            flat_output = agent_output.model_dump(exclude={"output"}) if hasattr(agent_output, "model_dump") else dict(agent_output or {})

            transition_metadata = transition_result.get("transition_metadata", {}) or {}
            transition_metadata.update({
                "agent_output": flat_output.get("output", {}),
                "file_path": flat_output.get("file_path"),
            })
            transition_result["transition_metadata"] = transition_metadata

            raw_state = transition_result.get("state", current)
            state_enum = raw_state if isinstance(raw_state, AGENT) else AGENT(raw_state)

            state = {
                **state,
                **transition_result,
                "state": state_enum,
                "file_path": transition_result.get("file_path") or state.get("file_path"),
                "_last_state": current,
                "state_output": flat_output,
            }

    @abstractmethod
    def _transition(self, state: dict, output: dict | None) -> dict:
        ...
