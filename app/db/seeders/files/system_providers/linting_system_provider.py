from app.providers.system_provider_base import SystemProviderBase

class LintingSystemProvider(SystemProviderBase):
    MAX_GENERATION_ATTEMPTS = 3

    def _transition(self, state: dict, state_output: dict | None) -> dict:
        retry_count = state.get("retry_count", 0)
        current = state.get("state")
        last = state.get("_last_state")
        result = state_output.get("result") if state_output else None

        if current == "start":
            return {
                "state": "code_stability",
                "reason": "initial stability check",
                "retry_count": 0
            }

        if current == "code_stability":
            if result == "pass":
                if last == "start":
                    return {
                        "state": "generate",
                        "reason": "initial stability passed, now generate",
                        "retry_count": retry_count
                    }
                return {
                    "state": "discriminate",
                    "reason": "post-generation stability passed, now discriminate",
                    "retry_count": retry_count
                }
            if last == "start":
                return {
                    "state": "end",
                    "reason": "initial stability failed—rejecting",
                    "retry_count": retry_count
                }
            retry_count += 1
            if retry_count >= self.MAX_GENERATION_ATTEMPTS:
                return {
                    "state": "end",
                    "reason": "max generation attempts reached",
                    "retry_count": retry_count
                }
            return {
                "state": "generate",
                "reason": "stability failed—retrying generation",
                "retry_count": retry_count
            }

        if current == "generate":
            return {
                "state": "code_stability",
                "reason": "post-generation stability check",
                "retry_count": retry_count
            }

        if current == "discriminate":
            if result == "pass":
                return {
                    "state": "end",
                    "reason": "discriminator accepted the change",
                    "retry_count": retry_count
                }
            retry_count += 1
            if retry_count >= self.MAX_GENERATION_ATTEMPTS:
                return {
                    "state": "end",
                    "reason": "max generation attempts reached",
                    "retry_count": retry_count
                }
            return {
                "state": "generate",
                "reason": "discriminator rejected—retry generate",
                "retry_count": retry_count
            }

        return {
            "state": "end",
            "reason": "unknown state, exiting",
            "retry_count": retry_count
        }
