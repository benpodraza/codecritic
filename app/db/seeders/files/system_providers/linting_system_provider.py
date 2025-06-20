from pathlib import Path
import json

from app.enums.fsm_enums import TRANSITION_REASON_TYPE, DECISION_TYPE
from app.enums.state_enums import STATE
from app.providers.system_provider_base import SystemProviderBase


class LintingSystemProvider(SystemProviderBase):
    def _transition(self, state: dict, state_output: dict | None) -> dict:
        current = STATE(state.get("state"))
        last = STATE(state.get("_last_state")) if state.get("_last_state") else None

        result = DECISION_TYPE.UNKNOWN
        score = 0.0

        if state_output and hasattr(state_output, "output"):
            output_obj = state_output.output
            if isinstance(output_obj, str):
                try:
                    output_obj = json.loads(output_obj)
                except Exception:
                    output_obj = {}

            if isinstance(output_obj, dict):
                result = output_obj.get("decision") or output_obj.get("result", DECISION_TYPE.UNKNOWN)
                score = output_obj.get("score", 0.0)
            else:
                result = getattr(output_obj, "decision", DECISION_TYPE.UNKNOWN)
                score = getattr(output_obj, "score", 0.0)

        transition = {}

        # START → GENERATE
        if current == STATE.START:
            transition = {
                "state": STATE.GENERATE,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION,
                "file_path": state.get("file_path")
            }


        # DISCRIMINATE (first pass) → CODE_STABILITY or GENERATE
        elif current == STATE.DISCRIMINATE and last == STATE.START:
            if score == 1.0:
                transition = {
                    "state": STATE.CODE_STABILITY,
                    "reason": TRANSITION_REASON_TYPE.EVALUATING,
                    "file_path": state.get("file_path")
                }
            else:
                transition = {
                    "state": STATE.GENERATE,
                    "reason": TRANSITION_REASON_TYPE.GENERATING,
                    "file_path": state.get("file_path")
                }

        # DISCRIMINATE (loop) → CODE_STABILITY or GENERATE
        elif current == STATE.DISCRIMINATE:
            if result == DECISION_TYPE.ACCEPTED:
                transition = {
                    "state": STATE.CODE_STABILITY,
                    "reason": TRANSITION_REASON_TYPE.EVALUATING,
                    "file_path": state.get("file_path")
                }
            elif result == DECISION_TYPE.IMPROVED:
                transition = {
                    "state": STATE.GENERATE,
                    "reason": TRANSITION_REASON_TYPE.GENERATING,
                    "file_path": state.get("file_path")
                }
            else:
                transition = {
                    "state": STATE.GENERATE,
                    "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL,
                    "file_path": state.get("file_path")
                }

        # GENERATE → DISCRIMINATE
        elif current == STATE.GENERATE:
            transition = {
                "state": STATE.DISCRIMINATE,
                "reason": TRANSITION_REASON_TYPE.EVALUATING,
                "file_path": state.get("file_path")
            }

        # CODE_STABILITY → END or fallback to GENERATE if rejected
        elif current == STATE.CODE_STABILITY:
            if result == DECISION_TYPE.ACCEPTED:
                transition = {
                    "state": STATE.END,
                    "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
                    "file_path": state.get("file_path")
                }
            else:
                transition = {
                    "state": STATE.GENERATE,
                    "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL,
                    "file_path": state.get("file_path")
                }

        if not transition:
            transition = {
                "state": STATE.END,
                "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE,
                "decision": result if isinstance(result, DECISION_TYPE) else DECISION_TYPE.UNKNOWN
            }

        return transition
