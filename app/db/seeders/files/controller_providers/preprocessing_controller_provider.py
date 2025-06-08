from app.enums.fsm_enums import DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.system_enums import SYSTEM
from app.providers.controller_provider_base import ControllerProviderBase

class PreprocessingControllerProvider(ControllerProviderBase):
    def _transition(self, state, sys_output):
        current = SYSTEM(state["state"])
        transition = {}

        # Transition from SYSTEM.START to SYSTEM.LINTING
        if current == SYSTEM.START:
            transition = {
                "state": SYSTEM.LINTING,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION,
            }
        # Transition from SYSTEM.LINTING to SYSTEM.END based on system output decision
        elif current == SYSTEM.LINTING:
            # Check the sys_output for decision and adjust transition reason accordingly
            if sys_output and hasattr(sys_output, "output") and isinstance(sys_output.output, dict):
                output_dict = sys_output.output
                decision = output_dict.get("decision", DECISION_TYPE.UNKNOWN)

                # Determine the transition reason based on the decision
                if decision == DECISION_TYPE.ACCEPTED:
                    transition = {
                        "state": SYSTEM.END,
                        "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
                    }
                elif decision == DECISION_TYPE.REJECTED:
                    transition = {
                        "state": SYSTEM.END,
                        "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL,
                    }
                else:
                    transition = {
                        "state": SYSTEM.END,
                        "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
                    }
                
                # Propagate the file path and decision to the next state
                transition["file_path"] = output_dict.get("file_path", state.get("file_path"))
                transition["decision"] = decision
            else:
                # Default case if no valid output is found
                transition = {
                    "state": SYSTEM.END,
                    "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
                }

        else:
            # Handle any other states that don't match SYSTEM.START or SYSTEM.LINTING
            transition = {
                "state": SYSTEM.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }

        return transition
