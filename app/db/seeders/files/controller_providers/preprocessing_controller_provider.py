from app.enums.fsm_enums import STATE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.controller_provider_base import ControllerProviderBase

class PreprocessingControllerProvider(ControllerProviderBase):
    def _transition(self, state, sys_output):
        current = STATE(state["state"])
        transition = {}

        if current == STATE.START:
            transition = {
                "state": STATE.PREPROCESS,
                "reason": TRANSITION_REASON_TYPE.KICKOFF,
            }
        elif current == STATE.PREPROCESS:
            transition = {
                "state": STATE.END.value,
                "reason": TRANSITION_REASON_TYPE.PREPROCESSING_COMPLETE,
            }
        else:
            transition = {
                "state": STATE.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }

        # 🔁 Propagate outputs from system FSM (without score)
        if sys_output:
            if hasattr(sys_output, "output") and isinstance(sys_output.output, dict):
                output_dict = sys_output.output
                transition["file_path"] = output_dict.get("file_path", state.get("file_path"))
                transition["decision"] = output_dict.get("decision", DECISION_TYPE.UNKNOWN)

        return transition
