from app.enums.controller_enums import CONTROLLER
from app.enums.fsm_enums import DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.program_provider_base import ProgramProviderBase

class CodeCriticProgramProvider(ProgramProviderBase):
    def _transition(self, state, ctrl_output):
        current = CONTROLLER(state["state"])
        transition = {}

        if current == CONTROLLER.START:
            return {
                "state": CONTROLLER.PREPROCESSING,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION,
            }

        elif current == CONTROLLER.PREPROCESSING:
            # Safely extract decision
            decision = getattr(ctrl_output, "decision", DECISION_TYPE.UNKNOWN)

            # Route based on decision
            if decision == DECISION_TYPE.ACCEPTED:
                transition = {
                    "state": CONTROLLER.END,
                    "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
                }
            elif decision == DECISION_TYPE.REJECTED:
                transition = {
                    "state": CONTROLLER.END,
                    "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL,
                }
            else:
                transition = {
                    "state": CONTROLLER.END,
                    "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
                }

            transition["file_path"] = getattr(ctrl_output, "file_path", state.get("file_path"))
            transition["decision"] = decision
            return transition

        else:
            return {
                "state": CONTROLLER.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }
    