from pathlib import Path
import json

from app.enums.fsm_enums import TRANSITION_REASON_TYPE
from app.enums.state_enums import STATE
from app.providers.system_provider_base import SystemProviderBase


class LintingSystemProvider(SystemProviderBase):
    SCORE_THRESHOLD = 0.85

    def _transition(self, state: dict, state_output: dict | None) -> dict:
        current = STATE(state.get("state"))
        last = STATE(state.get("_last_state")) if state.get("_last_state") else None

        result = None

        if state_output and hasattr(state_output, "output"):
            output_obj = state_output.output
            if isinstance(output_obj, str):
                try:
                    output_obj = json.loads(output_obj)
                except Exception:
                    output_obj = {}

            if isinstance(output_obj, dict):
                result = output_obj.get("decision") or output_obj.get("result")
            else:
                result = getattr(output_obj, "decision", None)

        transition = {}

        if current == STATE.START:
            transition = {
                "state": STATE.CODE_STABILITY,
                "reason": TRANSITION_REASON_TYPE.EVALUATING
            }

        elif current == STATE.CODE_STABILITY:
            if last == STATE.START:
                if result == "accept":
                    transition = {
                        "state": STATE.GENERATE,
                        "reason": TRANSITION_REASON_TYPE.PASSED,
                        "file_path": state.get("file_path")
                    }
                else:
                    transition = {
                        "state": STATE.END,
                        "reason": TRANSITION_REASON_TYPE.FAILED
                    }
            elif last == STATE.GENERATE:
                if result == "accept":
                    transition = {
                        "state": STATE.DISCRIMINATE,
                        "reason": TRANSITION_REASON_TYPE.PASSED,
                        "file_path": state.get("file_path")
                    }
                else:
                    transition = {
                        "state": STATE.GENERATE,
                        "reason": TRANSITION_REASON_TYPE.FAILED,
                        "file_path": state.get("file_path")
                    }

        elif current == STATE.GENERATE:
            transition = {
                "state": STATE.CODE_STABILITY,
                "reason": TRANSITION_REASON_TYPE.EVALUATING,
                "file_path": state.get("file_path")
            }

        elif current == STATE.DISCRIMINATE:
            if result == "accept":
                transition = {
                    "state": STATE.END,
                    "reason": TRANSITION_REASON_TYPE.PASSED,
                    "file_path": state.get("file_path")
                }
            else:
                transition = {
                    "state": STATE.GENERATE,
                    "reason": TRANSITION_REASON_TYPE.FAILED,
                    "file_path": state.get("file_path")
                }

        return transition
