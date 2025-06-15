from pathlib import Path
from app.enums.logging_enums import RunContext  # ✅ Add for context typing
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema


class BasicAgentProvider(AgentProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        raw_file_path = input.get("before") or input.get("file_name")
        relative_file_path = None

        if raw_file_path:
            try:
                relative_file_path = str(Path(raw_file_path).resolve().relative_to(Path.cwd()))
            except ValueError:
                relative_file_path = str(Path(raw_file_path).resolve())

        response = (
            "[AGENT_DECISION]accept[/AGENT_DECISION]\n"
            "[CONVERSATION_LOG_ENTRY]Basic agent executed successfully.[/CONVERSATION_LOG_ENTRY]\n"
            f"[CODE]{input.get('code', '# no code provided')}[/CODE]"
        )

        return AgentOutputSchema(
            response=response,
            log="Basic agent executed successfully.",
            decision="accept",
            snapshot_id=None,
            file_path=relative_file_path,
        )
