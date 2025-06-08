from pathlib import Path
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema


class CodeStabilityAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> AgentOutputSchema:
        score_result = self._score_provider.run(input, session_id=input["session_id"])

        raw_file_path = input.get("file_path") or input.get("file_name") or input.get("before")
        relative_file_path = None
        if raw_file_path:
            try:
                relative_file_path = str(Path(raw_file_path).resolve().relative_to(Path.cwd()))
            except ValueError:
                relative_file_path = str(Path(raw_file_path).resolve())

        if score_result.value >= 1.0:
            return AgentOutputSchema(
                response="""[AGENT_DECISION]accept[/AGENT_DECISION]
[CONVERSATION_LOG_ENTRY]Code passed all stability checks.[/CONVERSATION_LOG_ENTRY]""",
                log="Code passed all stability checks.",
                decision="accept",
                snapshot_id=None,
                file_path=relative_file_path,
                score=score_result.value
            )

        return AgentOutputSchema(
            response=f"""[AGENT_DECISION]reject[/AGENT_DECISION]
[CONVERSATION_LOG_ENTRY]Failed stability checks: {score_result.components}[/CONVERSATION_LOG_ENTRY]""",
            log=f"Failed stability checks: {score_result.components}",
            decision="reject",
            snapshot_id=None,
            file_path=relative_file_path,
            score=score_result.value
        )
