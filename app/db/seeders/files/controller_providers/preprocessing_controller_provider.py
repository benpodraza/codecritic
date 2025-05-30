from app.providers.controller_provider_base import ControllerProviderBase

class PreprocessingControllerProvider(ControllerProviderBase):
    def _transition(self, state, sys_output):
        if state["state"] == "start":
            return {"state": "preprocess", "reason": "kickoff"}
        if state["state"] == "preprocess":
            return {"state": "end", "reason": "after preprocessing"}
        return {"state": "end", "reason": "fallback"}