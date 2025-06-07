from __future__ import annotations
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict
from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.providers.fsm_provider_base import FSMProviderBase
from app.db.schemas import StateOutputSchema
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
        root = src.name.partition('.')[0]
        self.working_file = working_dir / f"{root}.__state_{timestamp}{src.suffix}"
        shutil.copy(src, self.working_file)
        self._generated_files.append(self.working_file)

        state = {
            "state": "start",
            "file_path": str(self.working_file),
            "session_id": session_id,
            "system": input.get("system", "unknown"),
            "reason": input.get("reason", "start"),
            "steps": input.get("steps", 0),
            "retry_count": input.get("retry_count", 0),
            "_last_state": input.get("_last_state"),
            "decision": DECISION_TYPE.UNKNOWN
        }

        step_count = 0

        while True:
            current = state.get("state")

            if step_count >= max_steps:
                return StateOutputSchema(
                    state="end",
                    previous_state=current,
                    state_type=STATE_TYPE.END,
                    decision=DECISION_TYPE.REJECT,
                    steps=step_count,
                    max_steps=max_steps,
                    summary=f"Max steps ({max_steps}) reached",
                    output=state,
                    provider_name=self._config.name
                )

            if current == "end":
                if self.score_provider:
                    best_file = select_best_file_by_score(
                        file_a=state["file_path"],
                        file_b=self.incoming_file,
                        score_provider=self.score_provider,
                        system=state.get("system", "unknown"),
                        session_id=session_id
                    )

                    final_path = Path("working_files") / f"final_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
                    shutil.copy(Path(best_file), final_path)
                    state["file_path"] = str(final_path)

                    # 🧼 Clean up final_* and *_stripped files except the one we just copied
                    for f in Path("working_files").glob("final_*.py"):
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


                return StateOutputSchema(
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
                transition = self._transition(state, None)
                state.update(transition, _last_state="start")
                continue

            agent = self.agent_providers.get(current)
            agent_output = agent.run(input=state, session_id=session_id) if agent else None

            transition_result = self._transition(state, agent_output)

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

            state = {
                **state,
                **transition_result,
                "file_path": transition_result.get("file_path") or state.get("file_path"),
                "score": transition_result.get("score") or getattr(agent_output, "score", None),
                "_last_state": current,
                "state_output": flat_output,
            }
