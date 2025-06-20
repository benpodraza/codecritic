import uuid
from datetime import datetime

from app.enums.fsm_enums import DECISION_TYPE
from app.enums.logging_enums import RunContext
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.utilities.diff_utils import summarize_diff
from app.utilities.metadata.snapshots.snapshot_archive import SnapshotArchive
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()
LINTING_PASS_THRESHOLD = 0.85

class LintingDiscriminatorAgentProvider(AgentProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        snapshot = SnapshotArchive(self._engine).read_latest(file_log_id=self._file_log_id)

        if not snapshot:
            full_log = "No snapshot found."
            return AgentOutputSchema(
                decision=DECISION_TYPE.REJECTED,
                log=full_log,
                response=(
                    f"[AGENT_DECISION]reject[/AGENT_DECISION]\n"
                    f"[CONVERSATION_LOG_ENTRY]{full_log}[/CONVERSATION_LOG_ENTRY]"
                ),
                file_path=None,
                score=None
            )

        before_code = snapshot["before"]
        after_code = snapshot["after"]
        before_path = snapshot["before_path"]
        after_path = snapshot["after_path"]

        before_result = self._score_provider.run(
            {"file_path": before_path},
            context=self.fork_context()
        )
        after_result = self._score_provider.run(
            {"file_path": after_path},
            context=self.fork_context()
        )

        before_score = before_result.value
        after_score = after_result.value

        if before_code == after_code:
            decision = DECISION_TYPE.ACCEPTED if before_score >= LINTING_PASS_THRESHOLD else DECISION_TYPE.REJECTED
            full_log = (
                "No meaningful change, but score already passing."
                if decision == DECISION_TYPE.ACCEPTED
                else "No meaningful change and score below threshold."
            )
            return AgentOutputSchema(
                decision=decision,
                log=full_log,
                response=(
                    f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                    f"[CONVERSATION_LOG_ENTRY]{full_log}[/CONVERSATION_LOG_ENTRY]"
                ),
                file_path=before_path,
                score=before_score
            )

        summary = summarize_diff(before_code, after_code).strip()
        if not summary:
            decision = DECISION_TYPE.ACCEPTED if before_score >= LINTING_PASS_THRESHOLD else DECISION_TYPE.REJECTED
            full_log = (
                "Diff could not be summarized, but prior version passes."
                if decision == DECISION_TYPE.ACCEPTED
                else "Diff could not be summarized and prior version fails."
            )
            return AgentOutputSchema(
                decision=decision,
                log=full_log,
                response=(
                    f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                    f"[CONVERSATION_LOG_ENTRY]{full_log}[/CONVERSATION_LOG_ENTRY]"
                ),
                file_path=before_path,
                score=before_score
            )

        after_components = getattr(after_result, "components", {})
        violation_msgs = []

        def get_violations(field) -> list[str]:
            val = getattr(after_components, field, None)
            if isinstance(val, list):
                return val
            if isinstance(val, int):
                return [f"{val} issues"]
            return []

        def append_messages(name: str, msgs: list[str]):
            if msgs:
                joined = "\n    - " + "\n    - ".join(msgs)
                violation_msgs.append(f"{name}:\n{joined}")

        append_messages("ruff", get_violations("ruff_violations"))
        append_messages("black", get_violations("black_violations"))
        append_messages("mypy", get_violations("mypy_violations"))

        violations_summary = (
            f"\n\n⚠️ Remaining violations:\n\n" + "\n\n".join(violation_msgs)
            if violation_msgs else "No Remaining violations"
        )

        if after_score >= LINTING_PASS_THRESHOLD and after_score >= before_score:
            decision = DECISION_TYPE.ACCEPTED
            chosen_code = after_code
            chosen_path = after_path
            score = after_score
        elif after_score < LINTING_PASS_THRESHOLD and after_score > before_score:
            decision = DECISION_TYPE.IMPROVED
            chosen_code = after_code
            chosen_path = after_path
            score = after_score
        else:
            decision = DECISION_TYPE.REJECTED
            chosen_code = before_code
            chosen_path = before_path
            score = before_score

        temp_filename = f"temp_agent_{datetime.now().strftime('%H%M%S%f')[:10]}.py"
        fm.copy(FILETYPE.SNAPSHOT, chosen_path, FILETYPE.WORKING, dst_filename=temp_filename)

        full_log = (
            f"✅ Score improved from {before_score:.2f} to {after_score:.2f} and passes threshold."
            f"{violations_summary}\n\n{summary}"
        )

        return AgentOutputSchema(
            decision=decision,
            log=full_log,
            response=(
                f"[AGENT_DECISION]{decision}[/AGENT_DECISION]\n"
                f"[CONVERSATION_LOG_ENTRY]{full_log}[/CONVERSATION_LOG_ENTRY]"
            ),
            file_path=temp_filename,
            score=score
        )
