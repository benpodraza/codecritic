from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from app.utilities.diff_utils import summarize_diff

class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> AgentOutputSchema:
        snapshot = read_latest_snapshot(session_id=self._session_id)
        if not snapshot:
            return AgentOutputSchema(
                response="[AGENT_DECISION]reject[/AGENT_DECISION]",
                log="No snapshot found.",
                decision="reject",
                snapshot_id=None
            )

        before, after = snapshot["before"], snapshot["after"]
        if before == after:
            return AgentOutputSchema(
                response="[AGENT_DECISION]reject[/AGENT_DECISION]",
                log="No meaningful change.",
                decision="reject",
                snapshot_id=None
            )

        summary = summarize_diff(before, after).strip()
        if not summary:
            return AgentOutputSchema(
                response="[AGENT_DECISION]reject[/AGENT_DECISION]",
                log="Diff could not be summarized.",
                decision="reject",
                snapshot_id=None
            )

        return AgentOutputSchema(
            response="[AGENT_DECISION]accept[/AGENT_DECISION]",
            log=summary,
            decision="accept",
            snapshot_id=None
        )
