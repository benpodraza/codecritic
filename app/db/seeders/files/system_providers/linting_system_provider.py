from pathlib import Path
from app.enums.fsm_enums import DECISION_TYPE
from app.providers.system_provider_base import SystemProviderBase
import json


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
                "reason": "initial stability check"
            }

        elif current == "code_stability":
            if last == "start":
                if result == "accept":
                    transition = {
                        "state": "generate",
                        "reason": "initial stability passed, now generate",
                        "file_path": state.get("file_path")
                    }
                else:
                    transition = {
                        "state": "end",
                        "reason": "initial stability failed—rejecting original code",
                        "decision": DECISION_TYPE.REJECT
                    }
            elif last == "generate":
                if result == "accept":
                    transition = {
                        "state": "discriminate",
                        "reason": "post-generation stability passed, now discriminate",
                        "file_path": state.get("file_path")
                    }
                else:
                    transition = {
                        "state": "generate",
                        "reason": "stability failed—retrying generation",
                        "file_path": state.get("file_path")
                    }

        elif current == "generate":
            transition = {
                "state": "code_stability",
                "reason": "post-generation stability check",
                "file_path": state.get("file_path")
            }

        elif current == "discriminate":
            if result == "accept":
                transition = {
                    "state": "end",
                    "reason": "discriminator accepted generation",
                    "file_path": state.get("file_path")
                }
            else:
                transition = {
                    "state": "generate",
                    "reason": "discriminator rejected—retrying generation",
                    "file_path": state.get("file_path")
                }
        
        return transition