from datetime import datetime, timezone
from pathlib import Path
from abc import abstractmethod

from app.enums.logging_enums import LogType
from app.providers.base_provider import BaseProvider
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter
from app.db.schemas import AgentConversationLogSchema

class AgentProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        engine=None,
        agent_engine=None,
        prompt_provider=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
    ):
        super().__init__(config=config, engine=engine)
        self._agent_engine = agent_engine
        self._prompt_provider = prompt_provider
        self._context_provider = context_provider
        self._score_provider = score_provider
        self._tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> str:
        output = self._run(input)

        self._log.debug(f"🐛 _run_provider called for: {self.config.name if self.config else 'unknown'}")

        # === Extract structured blocks ===
        code_block = self._extract_block(output, "[CODE]", "[/CODE]") or (
            output.strip() if input.get("before") else None
        )
        log_content = self._extract_block(output, "[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")

        # === Write snapshot ===
        file_path = input.get("before") or input.get("file_path") or (self.config.config or {}).get("before")
        if file_path and code_block:
            before_path = Path(file_path).resolve()
            if before_path.exists():
                snapshot_path = SnapshotWriter().write_snapshot(
                    before=before_path.read_text(encoding="utf-8"),
                    after=code_block,
                    session_id=self._session_id,
                )
                self._snapshot_id = snapshot_path
                self._log.debug(f"📦 Snapshot written to: {snapshot_path}")
            else:
                self._log.warning(f"❌ Snapshot skipped: file does not exist → {before_path}")

        # === Log conversation entry ===
        if log_content:
            self.logger.write(LogType.AGENT_CONVERSATION, AgentConversationLogSchema(
                session_id=self._session_id,
                system=self._system,
                agent_provider_config_id=self.config.id if self.config else -1,
                agent_name=self.config.name if self.config else "unknown",
                content=log_content,
                timestamp=datetime.now(timezone.utc),
            ))
            self._log.debug("✅ AGENT_CONVERSATION log write complete")

        return output

    def _extract_block(self, text: str, start_tag: str, end_tag: str) -> str | None:
        start = text.find(start_tag)
        end = text.find(end_tag)
        if start != -1 and end != -1 and start < end:
            return text[start + len(start_tag):end].strip()
        return None

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
