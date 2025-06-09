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
            # Check sys_output directly for decision
            if sys_output:
                # Directly check for 'decision' attribute in sys_output
                decision = sys_output.decision if hasattr(sys_output, 'decision') else DECISION_TYPE.UNKNOWN

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

                # Propagate the decision and file path to the next state
                transition["file_path"] = sys_output.file_path if hasattr(sys_output, 'file_path') else state.get("file_path")
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
