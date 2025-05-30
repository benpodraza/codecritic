# extensions/codecritic_program_provider.py

from app.providers.program_provider_base import ProgramProviderBase

class CodeCriticProgramProvider(ProgramProviderBase):
    def _transition(self, state, ctrl_output):
        if state["state"] == "start":
            return {"state": "preprocessing", "reason": "start of program"}

        if state["state"] == "preprocessing":
            return {"state": "end", "reason": "preprocessing complete"}

        return {"state": "end", "reason": "unexpected state"}
