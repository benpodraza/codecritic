from pathlib import Path
import json

from app.enums.fsm_enums import TRANSITION_REASON_TYPE, DECISION_TYPE
from app.enums.state_enums import STATE
from app.providers.system_provider_base import SystemProviderBase


class LintingSystemProvider(SystemProviderBase):
    SCORE_THRESHOLD = 0.85

    def _transition(self, state: dict, state_output: dict | None) -> dict:
        current = STATE(state.get("state"))
        last = STATE(state.get("_last_state")) if state.get("_last_state") else None

        result = DECISION_TYPE.UNKNOWN  # Default to unknown if no decision

        if state_output and hasattr(state_output, "output"):
            output_obj = state_output.output
            if isinstance(output_obj, str):
                try:
                    output_obj = json.loads(output_obj)
                except Exception:
                    output_obj = {}

            if isinstance(output_obj, dict):
                result = output_obj.get("decision") or output_obj.get("result", DECISION_TYPE.UNKNOWN)
            else:
                result = getattr(output_obj, "decision", DECISION_TYPE.UNKNOWN)

        transition = {}

        # Transition from START state
        if current == STATE.START:
            transition = {
                "state": STATE.CODE_STABILITY,
                "reason": TRANSITION_REASON_TYPE.EVALUATING
            }

        # Transition from CODE_STABILITY state
        elif current == STATE.CODE_STABILITY:
            if last == STATE.START:
                # If decision is ACCEPTED, proceed to GENERATE
                if result == DECISION_TYPE.ACCEPTED:
                    transition = {
                        "state": STATE.GENERATE,
                        "reason": TRANSITION_REASON_TYPE.GENERATING,
                        "file_path": state.get("file_path")
                    }
                # If decision is REJECTED, transition to END
                else:
                    transition = {
                        "state": STATE.END,
                        "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL
                    }
            elif last == STATE.GENERATE:
                # If decision is ACCEPTED, move to DISCRIMINATE
                if result == DECISION_TYPE.ACCEPTED:
                    transition = {
                        "state": STATE.DISCRIMINATE,
                        "reason": TRANSITION_REASON_TYPE.EVALUATING,
                        "file_path": state.get("file_path")
                    }
                # If decision is REJECTED, stay in GENERATE state
                else:
                    transition = {
                        "state": STATE.GENERATE,
                        "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL,
                        "file_path": state.get("file_path")
                    }

        # Transition from GENERATE state
        elif current == STATE.GENERATE:
            transition = {
                "state": STATE.CODE_STABILITY,
                "reason": TRANSITION_REASON_TYPE.EVALUATING,
                "file_path": state.get("file_path")
            }

        # Transition from DISCRIMINATE state
        elif current == STATE.DISCRIMINATE:
            if result == DECISION_TYPE.ACCEPTED:
                transition = {
                    "state": STATE.END,
                    "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
                    "file_path": state.get("file_path")
                }
            # Handle IMPROVED case: revert back to GENERATE if the code was improved
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

        return transition
