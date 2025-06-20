from pathlib import Path
from app.enums.logging_enums import RunContext
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.utilities.file_management.file_utils import get_file_manager

fm = get_file_manager()

class BasicAgentProvider(AgentProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        raw_file_path = input.get("before") or input.get("file_name")
        relative_file_path = None

        if raw_file_path:
            try:
                ftype = fm.resolve_existing_filetype(raw_file_path)
                abs_path = fm.resolve(ftype, raw_file_path)
                relative_file_path = str(abs_path.relative_to(Path.cwd()))
            except Exception:
                # fallback: use raw_file_path as-is if not resolvable
                relative_file_path = raw_file_path

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
