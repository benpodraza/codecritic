from app.enums.fsm_enums import DECISION_TYPE
from app.providers.program_provider_base import ProgramProviderBase

class CodeCriticProgramProvider(ProgramProviderBase):
    def _transition(self, state, ctrl_output):
        transition = {}

        if state["state"] == "start":
            transition = {
                "state": "preprocessing",
                "reason": "start of program"
            }

        elif state["state"] == "preprocessing":
            transition = {
                "state": "end",
                "reason": "preprocessing complete"
            }

        else:
            transition = {
                "state": "end",
                "reason": "unexpected state"
            }

        # 🔁 Propagate controller output fields
        if ctrl_output:
            if hasattr(ctrl_output, "output") and isinstance(ctrl_output.output, dict):
                output_dict = ctrl_output.output
                transition["file_path"] = output_dict.get("file_path") or state.get("file_path")
                transition["decision"] = output_dict.get("decision", DECISION_TYPE.UNKNOWN)
                transition["score"] = output_dict.get("score")

        return transition
