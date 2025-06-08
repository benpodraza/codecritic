from app.enums.fsm_enums import STATE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.program_provider_base import ProgramProviderBase

class CodeCriticProgramProvider(ProgramProviderBase):
    def _transition(self, state, ctrl_output):
        current = STATE(state["state"])
        transition = {}

        if current == STATE.START:
            transition = {
                "state": STATE.PREPROCESS,
                "reason": TRANSITION_REASON_TYPE.PROGRAM_INIT,
            }

        elif current == STATE.PREPROCESS:
            transition = {
                "state": STATE.END,
                "reason": TRANSITION_REASON_TYPE.PREPROCESSING_COMPLETE,
            }

        else:
            transition = {
                "state": STATE.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
            }

        # 🔁 Propagate controller output fields (minus score)
        if ctrl_output:
            if hasattr(ctrl_output, "output") and isinstance(ctrl_output.output, dict):
                output_dict = ctrl_output.output
                transition["file_path"] = output_dict.get("file_path") or state.get("file_path")
                transition["decision"] = output_dict.get("decision", DECISION_TYPE.UNKNOWN)

        return transition
