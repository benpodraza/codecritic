from __future__ import annotations
from pathlib import Path
import uuid

from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from app.utilities.diff_utils import summarize_diff

LINTING_PASS_THRESHOLD = 0.85

class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def _run(self, input: dict) -> AgentOutputSchema:
        snapshot = read_latest_snapshot(session_id=self._session_id)

        if not snapshot:
            return AgentOutputSchema(
                decision="reject",
                log="No snapshot found.",
                response=(
                    "[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                    "[CONVERSATION_LOG_ENTRY]No snapshot found.[/CONVERSATION_LOG_ENTRY]"
                ),
                file_path=None,
                score=None
            )

        # Extract both content and paths
        before_code = snapshot["before"]
        after_code = snapshot["after"]
        before_path = snapshot["before_path"]
        after_path = snapshot["after_path"]

        before_score = self._score_provider.run({"file_path": before_path}, session_id=self._session_id).value
        after_score = self._score_provider.run({"file_path": after_path}, session_id=self._session_id).value

        if before_code == after_code:
            if before_score >= LINTING_PASS_THRESHOLD:
                return AgentOutputSchema(
                    decision="accept",
                    log="No meaningful change, but score already passing.",
                    response=(
                        "[AGENT_DECISION]accept[/AGENT_DECISION]\n"
                        "[CONVERSATION_LOG_ENTRY]No meaningful change, but score already passing.[/CONVERSATION_LOG_ENTRY]"
                    ),
                    file_path=before_path,
                    score=before_score
                )
            else:
                return AgentOutputSchema(
                    decision="reject",
                    log="No meaningful change and score below threshold.",
                    response=(
                        "[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                        "[CONVERSATION_LOG_ENTRY]No meaningful change and score below threshold.[/CONVERSATION_LOG_ENTRY]"
                    ),
                    file_path=before_path,
                    score=before_score
                )

        summary = summarize_diff(before_code, after_code).strip()
        if not summary:
            if before_score >= LINTING_PASS_THRESHOLD:
                return AgentOutputSchema(
                    decision="accept",
                    log="Diff not available, but prior version passes.",
                    response=(
                        "[AGENT_DECISION]accept[/AGENT_DECISION]\n"
                        "[CONVERSATION_LOG_ENTRY]Diff could not be summarized, but prior version passes.[/CONVERSATION_LOG_ENTRY]"
                    ),
                    file_path=before_path,
                    score=before_score
                )
            else:
                return AgentOutputSchema(
                    decision="reject",
                    log="Diff could not be summarized and prior version fails.",
                    response=(
                        "[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                        "[CONVERSATION_LOG_ENTRY]Diff could not be summarized and prior version fails.[/CONVERSATION_LOG_ENTRY]"
                    ),
                    file_path=before_path,
                    score=before_score
                )

        # Determine winner based on score and threshold
        if after_score > before_score and after_score >= LINTING_PASS_THRESHOLD:
            decision = "accept"
            chosen_code = after_code
            score = after_score
        elif before_score >= LINTING_PASS_THRESHOLD:
            decision = "accept"
            chosen_code = before_code
            score = before_score
        else:
            decision = "reject"
            chosen_code = after_code
            score = after_score

        # Write chosen_code to disk for downstream use
        output_path = Path("working_files") / f"{uuid.uuid4().hex}.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(chosen_code, encoding="utf-8")

        return AgentOutputSchema(
            decision=decision,
            log=summary,
            response=(
                f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                f"[CONVERSATION_LOG_ENTRY]{summary}[/CONVERSATION_LOG_ENTRY]"
            ),
            file_path=str(output_path),
            score=score
        )
