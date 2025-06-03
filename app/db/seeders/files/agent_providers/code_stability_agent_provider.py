from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema

class CodeStabilityAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> AgentOutputSchema:
        score_result = self._score_provider.run(input, session_id=input["session_id"])
        if score_result.value >= 1.0:
            return AgentOutputSchema(
                response="[AGENT_DECISION]accept[/AGENT_DECISION]",
                log="Code passed all stability checks.",
                decision="accept",
                snapshot_id=None
            )

        return AgentOutputSchema(
            response="[AGENT_DECISION]reject[/AGENT_DECISION]",
            log=f"Failed stability checks: {score_result.components}",
            decision="reject",
            snapshot_id=None
        )
