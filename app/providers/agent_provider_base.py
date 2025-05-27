# app/providers/agent_provider_base.py

from datetime import datetime, timezone
from pathlib import Path
from abc import abstractmethod

from app.enums.logging_enums import LogType
from app.providers.base_provider import BaseProvider
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter
from app.db.schemas import AgentConversationLogSchema

class AgentProviderBase(BaseProvider):
    """Agent provider that wraps _run with snapshot and structured log logic."""

    def _run_provider(self, input: dict) -> str:
        output = self._run(input)

        self._log.debug(f"🐛 _run_provider called for: {self.config.name if self.config else 'unknown'}")

        code_block = None
        log_content = None

        #  Extract [CODE] block if present
        code_start = output.find("[CODE]")
        code_end = output.find("[/CODE]")
        if code_start != -1 and code_end != -1 and code_start < code_end:
            code_block = output[code_start + 6 : code_end].strip()
        #  FALLBACK: if we have a 'before' path, treat the whole output as the code
        elif input.get("before"):
            code_block = output.strip()

        #  Extract [CONVERSATION_LOG_ENTRY] if present
        log_start = output.find("[CONVERSATION_LOG_ENTRY]")
        log_end   = output.find("[/CONVERSATION_LOG_ENTRY]")
        if log_start != -1 and log_end != -1 and log_start < log_end:
            log_content = output[log_start + 24 : log_end].strip()

        #  Determine the file to snapshot
        file_path = input.get("before") or (self.config.config or {}).get("before")

        #  Write snapshot if we have both a before-file and produced code
        if file_path and code_block:
            before_path = Path(file_path)
            if not before_path.is_absolute():
                before_path = Path.cwd() / before_path

            print(f"📄 Final BEFORE PATH: {before_path}")

            if before_path.exists():
                snapshot_path = SnapshotWriter().write_snapshot(
                    before=before_path.read_text(encoding="utf-8"),
                    after=code_block,
                    session_id=self._session_id,
                    agent_name=self.config.name,
                    file_path=str(before_path),
                )
                self._snapshot_id = snapshot_path
                self._log.debug(f"📦 Snapshot written to: {snapshot_path}")
            else:
                self._log.warning(f"❌ Snapshot skipped: input file does not exist → {before_path}")

        #  Always log any conversation log entry
        if log_content:
            log = AgentConversationLogSchema(
                session_id=self._session_id,
                system=self._system,
                agent_provider_config_id=self.config.id if self.config else -1,
                agent_name=self.config.name if self.config else "unknown",
                content=log_content,
                timestamp=datetime.now(timezone.utc)
            )
            self.logger.write(LogType.AGENT_CONVERSATION, log)
            self._log.debug("✅ AGENT_CONVERSATION log write complete")

        return output

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
