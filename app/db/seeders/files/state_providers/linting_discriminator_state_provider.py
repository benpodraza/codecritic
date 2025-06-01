from app.providers.state_provider_base import StateProviderBase

class LintingDiscriminatorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        current = state["state"]

        if current == "start":
            return {
                "state": "discriminate",
                "reason": "begin discriminator step"
            }

        if current == "discriminate":
            if agent_output and "[AGENT_DECISION]accept" in agent_output:
                return {
                    "state": "end",
                    "reason": "discriminator accepted the change",
                    "result": "pass"
                }
            return {
                "state": "end",
                "reason": "discriminator rejected the change",
                "result": "fail"
            }

        return {
            "state": "end",
            "reason": "invalid discriminator state"
        }
