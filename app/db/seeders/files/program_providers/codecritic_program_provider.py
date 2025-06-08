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
            # Check the ctrl_output for decision and adjust transition reason accordingly
            if ctrl_output and hasattr(ctrl_output, "output") and isinstance(ctrl_output.output, dict):
                output_dict = ctrl_output.output
                decision = output_dict.get("decision", DECISION_TYPE.UNKNOWN)

                # Determine the transition reason based on the decision
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

                # Propagate the file path and decision to the next state
                transition["file_path"] = output_dict.get("file_path", state.get("file_path"))
                transition["decision"] = decision
            else:
                # If no valid decision is found, assume a custom rule transition
                transition = {
                    "state": CONTROLLER.END,
                    "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
                }

        else:
            transition = {
                "state": CONTROLLER.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }

        return transition
