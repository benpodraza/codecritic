from app.enums.controller_enums import CONTROLLER
from app.enums.fsm_enums import DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.program_provider_base import ProgramProviderBase

class CodeCriticProgramProvider(ProgramProviderBase):
    def _transition(self, state, ctrl_output):
        current = CONTROLLER(state["state"])
        transition = {}

        if current == CONTROLLER.START:
            transition = {
                "state": CONTROLLER.PREPROCESSING,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION,
            }

        elif current == CONTROLLER.PREPROCESSING:
            transition = {
                "state": CONTROLLER.END,
                "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
            }

        else:
            transition = {
                "state": CONTROLLER.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }

        if ctrl_output:
            if hasattr(ctrl_output, "output") and isinstance(ctrl_output.output, dict):
                output_dict = ctrl_output.output
                transition["file_path"] = output_dict.get("file_path") or state.get("file_path")
                transition["decision"] = output_dict.get("decision", DECISION_TYPE.UNKNOWN)

        return transition
