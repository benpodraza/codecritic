from app.enums.fsm_enums import DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.system_enums import SYSTEM
from app.providers.controller_provider_base import ControllerProviderBase

class PreprocessingControllerProvider(ControllerProviderBase):
    def _transition(self, state, sys_output):
        current = SYSTEM(state["state"])
        transition = {}

        if current == SYSTEM.START:
            transition = {
                "state": SYSTEM.LINTING,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION,
            }
        elif current == SYSTEM.LINTING:
            transition = {
                "state": SYSTEM.END,
                "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
            }
        else:
            transition = {
                "state": SYSTEM.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }

        # 🔁 Propagate outputs from system FSM (without score)
        if sys_output:
            if hasattr(sys_output, "output") and isinstance(sys_output.output, dict):
                output_dict = sys_output.output
                transition["file_path"] = output_dict.get("file_path", state.get("file_path"))
                transition["decision"] = output_dict.get("decision", DECISION_TYPE.UNKNOWN)

        return transition
