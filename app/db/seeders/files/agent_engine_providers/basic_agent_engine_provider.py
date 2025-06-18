from app.enums.logging_enums import RunContext
from app.db.schemas import AgentEngineOutput
from app.providers.agent_engine_provider_base import AgentEngineProviderBase

class BasicAgentEngineProvider(AgentEngineProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentEngineOutput:
        if not self.prompt_provider:
            raise ValueError("Prompt provider is required to extract engine output.")

        # Simulate a basic LLM response format
        response = """[AGENT_DECISION]accept[/AGENT_DECISION]
[CONVERSATION_LOG_ENTRY]Basic agent executed successfully.[/CONVERSATION_LOG_ENTRY]
[CODE]# no code provided[/CODE]"""

        token_count = len(response.split())
        cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

        extracted = self.prompt_provider._extract(response)

        return AgentEngineOutput(
            response=response,
            token_count=token_count,
            cost_usd=cost_usd,
            content=extracted.content,
            decision=extracted.decision,
            log=extracted.log
        )
