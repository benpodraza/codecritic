from app.enums.fsm_enums import DECISION_TYPE
from app.providers.controller_provider_base import ControllerProviderBase

class PreprocessingControllerProvider(ControllerProviderBase):
    def _transition(self, state, sys_output):
        transition = {}

        if state["state"] == "start":
            transition = {
                "state": "preprocess",
                "reason": "kickoff",
            }
        elif state["state"] == "preprocess":
            transition = {
                "state": "end",
                "reason": "after preprocessing",
            }
        else:
            transition = {
                "state": "end",
                "reason": "fallback",
            }

        # 🔁 Propagate outputs from system FSM
        if sys_output:
            if hasattr(sys_output, "output") and isinstance(sys_output.output, dict):
                output_dict = sys_output.output
                transition["file_path"] = output_dict.get("file_path", state.get("file_path"))
                transition["decision"] = output_dict.get("decision", DECISION_TYPE.UNKNOWN)
                transition["score"] = output_dict.get("score", None)

        return transition
