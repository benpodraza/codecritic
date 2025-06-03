from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase

class BasicAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict) -> AgentEngineOutput:
        response = f"[Basic Response] You said: {input.get('prompt', '')}"
        token_count = len(response.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000
        return AgentEngineOutput(response=response, token_count=token_count, cost_usd=cost_usd)
