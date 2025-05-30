from __future__ import annotations

from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
from pathlib import Path
import shutil
import json

from app.providers.base_provider import BaseProvider
from app.factories.controller_provider_factory import ControllerProviderFactory
from app.db.schemas import StateTransitionLogSchema, ProviderLogSchema
from app.enums.logging_enums import LogType

class ProgramProviderBase(BaseProvider):
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
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []
        self._controllers: Dict[str, object] = {}

        controller_cfg = config.config.get("controllers", {})
        for name, provider_id in controller_cfg.items():
            self._controllers[name] = ControllerProviderFactory.create(provider_id)

    def _run_provider(self, input: dict) -> dict:
        session_id = input.get("session_id")
        input_file = Path(input["file_name"])
        self.working_file = input_file.with_name(f"{input_file.stem}_working{input_file.suffix}")
        shutil.copy(input_file, self.working_file)

        state = {
            "state": "start",
            "file_name": str(input_file),
            "working_file": str(self.working_file),
            **input,
        }

        max_steps = 20
        step_count = 0

        while True:
            if step_count >= max_steps:
                state["state"] = "end"
                state["reason"] = f"max steps ({max_steps}) reached"
                break
            step_count += 1

            current = state.get("state")

            if current == "end":
                self.logger.write(LogType.PROVIDER, ProviderLogSchema(
                    session_id=session_id,
                    provider_id=self.config.id,
                    provider_type=self.__class__.__name__,
                    input=json.dumps(input),
                    output=json.dumps(state),
                    file_path=self.config.artifact_path,
                    timestamp=datetime.now(timezone.utc)
                ))
                return state

            if current == "start":
                state = {**state, **self.transition(state, None), "_last_state": "start"}
                continue

            controller = self._controllers.get(current)
            if not controller:
                raise ValueError(f"No controller registered for state: {current}")

            controller_input = {k: v for k, v in state.items() if k != "state"}
            output = controller.run(input=controller_input, session_id=session_id)

            transition_result = self.transition(state, output)
            flat_output = {k: v for k, v in output.items() if k != "output"}
            state = {**state, **transition_result, "_last_state": current, "output": flat_output}

        return state

    def transition(self, state: dict, controller_output: dict | None) -> dict:
        next_state = self._transition(state, controller_output)
        self.logger.write(LogType.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=state.get("session_id"),
            entity_type=self.__class__.__name__,
            entity_id=self.config.id,
            from_state=state.get("state"),
            to_state=next_state.get("state", "unknown"),
            reason=next_state.get("reason", "unspecified"),
            timestamp=datetime.now(timezone.utc)
        ))
        return next_state

    @abstractmethod
    def _transition(self, state: dict, controller_output: dict | None) -> dict:
        raise NotImplementedError
