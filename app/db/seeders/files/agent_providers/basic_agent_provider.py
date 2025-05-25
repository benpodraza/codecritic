from app.providers.agent_provider_base import AgentProviderBase

class BasicAgentProvider(AgentProviderBase):
    def _run(self, agent_config: dict) -> str:
        return f"[Agent] Executed with config: {agent_config}"
