from app.providers.agent_provider_base import AgentProviderBase
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from app.utilities.diff_utils import summarize_diff

class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def __init__(self, config=None, engine=None, **kwargs):
        super().__init__(config=config, engine=engine, **kwargs)

    def _run(self, input: dict) -> str:
        snapshot = read_latest_snapshot(session_id=self._session_id)
        if not snapshot:
            return (
                "[AGENT_DECISION]reject[/AGENT_DECISION]\n\n"
                "[CONVERSATION_LOG_ENTRY]\nNo snapshot found.\n[/CONVERSATION_LOG_ENTRY]"
            )

        before, after = snapshot["before"], snapshot["after"]
        if before == after:
            return (
                "[AGENT_DECISION]reject[/AGENT_DECISION]\n\n"
                "[CONVERSATION_LOG_ENTRY]\nNo meaningful change.\n[/CONVERSATION_LOG_ENTRY]"
            )

        summary = summarize_diff(before, after).strip()
        if not summary:
            return (
                "[AGENT_DECISION]reject[/AGENT_DECISION]\n\n"
                "[CONVERSATION_LOG_ENTRY]\nDiff could not be summarized.\n[/CONVERSATION_LOG_ENTRY]"
            )

        return (
            "[AGENT_DECISION]accept[/AGENT_DECISION]\n\n"
            f"[CONVERSATION_LOG_ENTRY]\n{summary}\n[/CONVERSATION_LOG_ENTRY]"
        )
