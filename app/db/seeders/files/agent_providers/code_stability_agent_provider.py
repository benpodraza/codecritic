from app.providers.agent_provider_base import AgentProviderBase
import json

class CodeStabilityAgentProvider(AgentProviderBase):
    def __init__(self, config=None, engine=None, score_provider=None, **kwargs):
        super().__init__(config=config, engine=engine, **kwargs)
        self.score_provider = score_provider

    def _run(self, input: dict) -> str:
        score_provider = self.score_provider
        result = score_provider.run(input, session_id=input["session_id"])
        if result.value >= 1.0:
            return (
                "[AGENT_DECISION]accept[/AGENT_DECISION]\n\n"
                "[CONVERSATION_LOG_ENTRY]\nCode passed all stability checks.\n[/CONVERSATION_LOG_ENTRY]"
            )

        return (
            "[AGENT_DECISION]reject[/AGENT_DECISION]\n\n"
            f"[CONVERSATION_LOG_ENTRY]\nFailed stability checks: {result.components}\n[/CONVERSATION_LOG_ENTRY]"
        )