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

        if result == "pass":
            result = "accept"

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
                session_id = state.get("session_id", "")
                system = state.get("system", "unknown")

                working_file = str(Path(self.working_file).resolve())
                original_file = str(Path(self.incoming_file).resolve())
                new_file = state_output.output.get("file_path") if state_output.output else None

                discriminator_score = state_output.output.get("score") if state_output.output else None

                working_score = self.score_provider.run(
                    {"file_path": working_file, "system": system},
                    session_id=session_id
                ).value

                original_score = self.score_provider.run(
                    {"file_path": original_file, "system": system},
                    session_id=session_id
                ).value

                scores = {
                    "discriminator": discriminator_score,
                    "working": working_score,
                    "original": original_score
                }

                best_label, best_score = max(scores.items(), key=lambda kv: kv[1])
                best_file = {
                    "discriminator": new_file,
                    "working": working_file,
                    "original": original_file
                }.get(best_label, working_file)

                if best_file is None:
                    best_file = working_file

                # 🧠 THIS IS THE POLICY ENFORCEMENT POINT
                self.working_file = str(Path(best_file).resolve())  # ← Update the working_file permanently

                if best_score >= self.SCORE_THRESHOLD:
                    transition = {
                        "state": "end",
                        "reason": f"best file = {best_label}, score = {best_score}",
                        "decision": DECISION_TYPE.ACCEPT if best_label != "original" else DECISION_TYPE.REJECT,
                        "score": best_score,
                        "file_path": best_file
                    }
                else:
                    transition = {
                        "state": "generate",
                        "reason": "all scores below threshold—retrying with best available file",
                        "file_path": best_file
                    }

            else:
                transition = {
                    "state": "generate",
                    "reason": "discriminator rejected—retrying generation",
                    "file_path": state.get("file_path")
                }
        
        return transition