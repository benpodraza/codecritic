from pathlib import Path
import json

from app.enums.fsm_enums import DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.system_provider_base import SystemProviderBase


class LintingSystemProvider(SystemProviderBase):
    SCORE_THRESHOLD = 0.85

    def _transition(self, state: dict, state_output: dict | None) -> dict:
        current = state.get("state")
        last = state.get("_last_state")

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

        if current == "start":
            transition = {
                "state": "code_stability",
                "reason": TRANSITION_REASON_TYPE.STABILITY_CHECK
            }

        elif current == "code_stability":
            if last == "start":
                if result == "accept":
                    transition = {
                        "state": "generate",
                        "reason": TRANSITION_REASON_TYPE.STABILITY_PASSED,
                        "file_path": state.get("file_path")
                    }
                else:
                    transition = {
                        "state": "end",
                        "reason": TRANSITION_REASON_TYPE.STABILITY_FAILED
                    }
            elif last == "generate":
                if result == "accept":
                    transition = {
                        "state": "discriminate",
                        "reason": TRANSITION_REASON_TYPE.POST_GEN_STABILITY_PASSED,
                        "file_path": state.get("file_path")
                    }
                else:
                    transition = {
                        "state": "generate",
                        "reason": TRANSITION_REASON_TYPE.POST_GEN_STABILITY_FAILED,
                        "file_path": state.get("file_path")
                    }

        elif current == "generate":
            transition = {
                "state": "code_stability",
                "reason": TRANSITION_REASON_TYPE.STABILITY_CHECK,
                "file_path": state.get("file_path")
            }

        elif current == "discriminate":
            if result == "accept":
                transition = {
                    "state": "end",
                    "reason": TRANSITION_REASON_TYPE.DISCRIMINATOR_ACCEPTED,
                    "file_path": state.get("file_path")
                }
            else:
                transition = {
                    "state": "generate",
                    "reason": TRANSITION_REASON_TYPE.DISCRIMINATOR_REJECTED,
                    "file_path": state.get("file_path")
                }

        return transition
