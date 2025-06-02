from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema

class BasicAgentProvider(AgentProviderBase):
    def _run(self, agent_config: dict) -> AgentOutputSchema:
        response = f"[Agent] Executed with config: {agent_config}"
        return AgentOutputSchema(
            response=response,
            log="Executed basic agent logic.",
            decision="unknown",
            snapshot_id=None
        )
