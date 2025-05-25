from app.providers.agent_engine_provider_base import AgentEngineProviderBase

class BasicAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, prompt: str) -> str:
        # Mock response for testing
        return f"[Basic Response] You said: {prompt}"
