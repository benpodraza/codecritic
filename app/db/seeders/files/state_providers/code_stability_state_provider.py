from app.providers.state_provider_base import StateProviderBase

class CodeStabilityStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        if state.get("state") == "start":
            return {"state": "code_stability", "reason": "entering stability check"}

        result = "pass" if agent_output and "[AGENT_DECISION]accept" in agent_output else "fail"
        return {
            "state": "end",
            "reason": "stability passed" if result == "pass" else "stability failed",
            "result": result
        }
