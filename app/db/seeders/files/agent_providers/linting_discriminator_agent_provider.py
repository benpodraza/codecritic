from app.providers.agent_provider_base import AgentProviderBase
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from app.utilities.diff_utils import summarize_diff

class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> str:
        snapshot = read_latest_snapshot(session_id=self._session_id)  # ✅ session-aware
        if not snapshot:
            return "[AGENT_DECISION]reject[/AGENT_DECISION]\n\n[CONVERSATION_LOG_ENTRY]\nNo snapshot found.\n[/CONVERSATION_LOG_ENTRY]"

        before, after = snapshot["before"], snapshot["after"]
        if before == after:
            return "[AGENT_DECISION]reject[/AGENT_DECISION]\n\n[CONVERSATION_LOG_ENTRY]\nNo meaningful change.\n[/CONVERSATION_LOG_ENTRY]"

        diff_summary = summarize_diff(before, after)

        decision = "accept" if diff_summary else "reject"

        return f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n\n[CONVERSATION_LOG_ENTRY]\n{diff_summary}\n[/CONVERSATION_LOG_ENTRY]"
