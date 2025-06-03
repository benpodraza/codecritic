from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from app.utilities.diff_utils import summarize_diff


class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> AgentOutputSchema:
        snapshot = read_latest_snapshot(session_id=self._session_id)

        if not snapshot:
            decision = "reject"
            log = "No snapshot found."
            response = (
                "[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                "[CONVERSATION_LOG_ENTRY]No snapshot found.[/CONVERSATION_LOG_ENTRY]"
            )
            return AgentOutputSchema(response=response, log=log, decision=decision, snapshot_id=None)

        before, after = snapshot["before"], snapshot["after"]

        if before == after:
            decision = "reject"
            log = "No meaningful change."
            response = (
                "[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                "[CONVERSATION_LOG_ENTRY]No meaningful change.[/CONVERSATION_LOG_ENTRY]"
            )
            return AgentOutputSchema(response=response, log=log, decision=decision, snapshot_id=None)

        summary = summarize_diff(before, after).strip()
        if not summary:
            decision = "reject"
            log = "Diff could not be summarized."
            response = (
                "[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                "[CONVERSATION_LOG_ENTRY]Diff could not be summarized.[/CONVERSATION_LOG_ENTRY]"
            )
            return AgentOutputSchema(response=response, log=log, decision=decision, snapshot_id=None)

        decision = "accept"
        log = summary
        response = (
            f"[AGENT_DECISION]accept[/AGENT_DECISION]\n"
            f"[CONVERSATION_LOG_ENTRY]{summary}[/CONVERSATION_LOG_ENTRY]"
        )
        return AgentOutputSchema(response=response, log=log, decision=decision, snapshot_id=None)
