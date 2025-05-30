
from app.providers.state_provider_base import StateProviderBase
from app.factories.agent_provider_factory import AgentProviderFactory

class LintingDiscriminatorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: str | None) -> dict:
        if agent_output and "[AGENT_DECISION]accept" in agent_output:
            return {"state": "end", "reason": "discriminator accepted the change"}
        return {"state": "end", "reason": "discriminator rejected the change"}