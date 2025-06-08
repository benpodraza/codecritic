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

        before_code = snapshot["before"]
        after_code = snapshot["after"]
        before_path = Path(snapshot["before_path"]).resolve()
        after_path = Path(snapshot["after_path"]).resolve()

        before_score = self._score_provider.run({"file_path": str(before_path)}, session_id=self._session_id).value
        after_score = self._score_provider.run({"file_path": str(after_path)}, session_id=self._session_id).value

        def safe_relative(path: Path) -> str:
            try:
                return str(path.relative_to(Path.cwd()))
            except ValueError:
                return str(path)

        if before_code == after_code:
            decision = "accept" if before_score >= LINTING_PASS_THRESHOLD else "reject"
            log_msg = (
                "No meaningful change, but score already passing."
                if decision == "accept"
                else "No meaningful change and score below threshold."
            )
            return AgentOutputSchema(
                decision=decision,
                log=log_msg,
                response=(
                    f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                    f"[CONVERSATION_LOG_ENTRY]{log_msg}[/CONVERSATION_LOG_ENTRY]"
                ),
                file_path=safe_relative(before_path),
                score=before_score
            )

        summary = summarize_diff(before_code, after_code).strip()
        if not summary:
            decision = "accept" if before_score >= LINTING_PASS_THRESHOLD else "reject"
            log_msg = (
                "Diff could not be summarized, but prior version passes."
                if decision == "accept"
                else "Diff could not be summarized and prior version fails."
            )
            return AgentOutputSchema(
                decision=decision,
                log=log_msg,
                response=(
                    f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                    f"[CONVERSATION_LOG_ENTRY]{log_msg}[/CONVERSATION_LOG_ENTRY]"
                ),
                file_path=safe_relative(before_path),
                score=before_score
            )

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
            file_path=safe_relative(output_path),
            score=score
        )
