from app.providers.state_provider_base import StateProviderBase

class LintingGeneratorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        current = state["state"]

        if current == "start":
            return {
                "state": "generate",
                "reason": "entering generation step"
            }

        if current == "generate":
            return {
                "state": "end",
                "reason": "generation complete"
            }

        return {
            "state": "end",
            "reason": "unknown state"
        }
