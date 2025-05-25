from app.providers.orchestrator_provider_base import OrchestratorProviderBase

class BasicOrchestratorProvider(OrchestratorProviderBase):
    def _run(self, input: dict) -> str:
        state = input.get("state")
        return f"Running orchestrator state: {state}"

    def _transition(self, state: dict) -> dict:
        current = state.get("state")
        states = self.config.config.get("states", [])
        if current not in states:
            raise ValueError(f"Invalid state: {current}")

        idx = states.index(current)
        next_state = states[idx + 1] if idx + 1 < len(states) else states[-1]
        return {**state, "state": next_state}