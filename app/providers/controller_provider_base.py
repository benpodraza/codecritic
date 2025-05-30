from __future__ import annotations
from abc import abstractmethod
from typing import Dict
from datetime import datetime, timezone
from pathlib import Path
import shutil, json

from app.providers.base_provider import BaseProvider
from app.factories.system_provider_factory import SystemProviderFactory
from app.db.schemas import StateTransitionLogSchema, ProviderLogSchema
from app.enums.logging_enums import LogType

class ControllerProviderBase(BaseProvider):
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
        self.score_provider   = score_provider
        self.tool_providers   = tool_providers or []

        # instantiate sub-systems
        self._systems: Dict[str, object] = {}
        for name, sys_id in (config.config or {}).get("systems", {}).items():
            self._systems[name] = SystemProviderFactory.create(sys_id)

    def _run_provider(self, input: dict) -> dict:
        sess = input.get("session_id")
        src  = Path(input["file_name"])
        self.working_file = src.with_name(f"{src.stem}_working{src.suffix}")
        shutil.copy(src, self.working_file)

        state = {
            "state":        "start",
            "file_path":    str(src),
            "working_file": str(self.working_file),
            **input,
        }

        while True:
            cur = state["state"]
            if cur == "end":
                # final provider log
                self.logger.write(LogType.PROVIDER, ProviderLogSchema(
                    session_id=sess,
                    provider_id=self.config.id,
                    provider_type=self.__class__.__name__,
                    input=json.dumps(input),
                    output=json.dumps(state),
                    file_path=self.config.artifact_path,
                    timestamp=datetime.now(timezone.utc)
                ))
                return state

            if cur == "start":
                nxt = self.transition(state, None)
                state.update(nxt, _last_state="start")
                continue

            # call the named sub-system
            sysprov = self._systems.get(cur)
            if not sysprov:
                raise ValueError(f"No system registered for state '{cur}'")

            # pass through everything except the `state` key
            inp = {k: v for k,v in state.items() if k != "state"}
            out = sysprov.run(input=inp, session_id=sess)

            nxt = self.transition(state, out)
            flat_output = {k: v for k, v in out.items() if k != "output"}
            state.update(nxt, _last_state=cur, output=flat_output)


    def transition(self, state: dict, sys_output: str|None) -> dict:
        nxt = self._transition(state, sys_output)
        self.logger.write(LogType.STATE_TRANSITION, StateTransitionLogSchema(
            session_id=state["session_id"],
            entity_type=self.__class__.__name__,
            entity_id=self.config.id,
            from_state=state["state"],
            to_state=nxt.get("state", "unknown"),
            reason=nxt.get("reason", "unspecified"),
            timestamp=datetime.now(timezone.utc)
        ))
        return nxt

    @abstractmethod
    def _transition(self, state: dict, sys_output: str|None) -> dict:
        """Implement your FSM logic in the extension."""
        ...
