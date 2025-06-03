from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema


class BasicAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> AgentOutputSchema:
        response = (
            "[AGENT_DECISION]accept[/AGENT_DECISION]\n"
            "[CONVERSATION_LOG_ENTRY]Basic agent executed successfully.[/CONVERSATION_LOG_ENTRY]\n"
            f"[CODE]{input.get('code', '# no code provided')}[/CODE]"
        )
        return AgentOutputSchema(
            response=response,
            log="Basic agent executed successfully.",
            decision="accept",
            snapshot_id=None
        )
