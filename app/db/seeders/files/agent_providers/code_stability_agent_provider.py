from pathlib import Path
from app.enums.fsm_enums import DECISION_TYPE
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.enums.logging_enums import RunContext  # needed to type context


class CodeStabilityAgentProvider(AgentProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        score_result = self._score_provider.run(input, context=self.fork_context())

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
                decision=DECISION_TYPE.ACCEPTED,
                snapshot_id=None,
                file_path=relative_file_path,
                score=score_result.value
            )

        return AgentOutputSchema(
            response=f"""[AGENT_DECISION]reject[/AGENT_DECISION]
[CONVERSATION_LOG_ENTRY]Failed stability checks: {score_result.components}[/CONVERSATION_LOG_ENTRY]""",
            log=f"Failed stability checks: {score_result.components}",
            decision=DECISION_TYPE.REJECTED,
            snapshot_id=None,
            file_path=relative_file_path,
            score=score_result.value
        )
