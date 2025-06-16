from pathlib import Path
import uuid
import shutil
from datetime import datetime

from app.enums.fsm_enums import DECISION_TYPE
from app.enums.logging_enums import RunContext
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from app.utilities.diff_utils import summarize_diff

LINTING_PASS_THRESHOLD = 0.85

class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        
        snapshot = read_latest_snapshot(session_id=self._session_id)

        if not snapshot:
            return AgentOutputSchema(
                decision=DECISION_TYPE.REJECTED,
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

        before_score = self._score_provider.run(
            {"file_path": str(before_path)},
            context=self.fork_context()
        ).value

        after_score = self._score_provider.run(
            {"file_path": str(after_path)},
            context=self.fork_context()
        ).value

        def safe_relative(path: Path) -> str:
            try:
                return str(path.relative_to(Path.cwd()))
            except ValueError:
                return str(path)

        if before_code == after_code:
            decision = DECISION_TYPE.ACCEPTED if before_score >= LINTING_PASS_THRESHOLD else DECISION_TYPE.REJECTED
            log_msg = (
                "No meaningful change, but score already passing."
                if decision == DECISION_TYPE.ACCEPTED
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

        # Summarize the diff if the code has changed
        summary = summarize_diff(before_code, after_code).strip()
        if not summary:
            decision = DECISION_TYPE.ACCEPTED if before_score >= LINTING_PASS_THRESHOLD else DECISION_TYPE.REJECTED
            log_msg = (
                "Diff could not be summarized, but prior version passes."
                if decision == DECISION_TYPE.ACCEPTED
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

        # Check the scores for acceptance or improvement
        if after_score >= LINTING_PASS_THRESHOLD and after_score >= before_score:
            decision = DECISION_TYPE.ACCEPTED
            chosen_code = after_code
            score = after_score
        elif after_score < LINTING_PASS_THRESHOLD and after_score > before_score:
            decision = DECISION_TYPE.IMPROVED
            chosen_code = after_code
            score = after_score
        else:
            decision = DECISION_TYPE.REJECTED
            chosen_code = before_code
            score = before_score

        # Promote improved file to a working path (if chosen_code came from after_code)
        temp_path = Path("working_files") / f"temp_agent_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        source_path = after_path if chosen_code == after_code else before_path
        shutil.copyfile(source_path, temp_path)

        return AgentOutputSchema(
            decision=decision,
            log=summary,
            response=(
                f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                f"[CONVERSATION_LOG_ENTRY]{summary}[/CONVERSATION_LOG_ENTRY]"
            ),
            file_path=safe_relative(temp_path),
            score=score
        )
