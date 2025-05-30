from app.providers.state_provider_base import StateProviderBase

class LintingGeneratorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        return {"state": "end", "reason": "generation complete"}
