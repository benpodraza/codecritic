from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from abc import abstractmethod
from sqlalchemy.orm import Session

from app.db.models import SnapshotMetrics
from app.enums.logging_enums import LOG_TYPE, RunContext
from app.enums.agent_enums import AGENT
from app.enums.fsm_enums import DECISION_TYPE
from app.providers.base_provider import BaseProvider
from app.utilities.metadata.footer.code_annnotation_utils import append_agent_note
from app.utilities.metadata.snapshots.analyze_code_metrics import analyze_code, compute_deltas
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter
from app.db.schemas import AgentConversationLogSchema, AgentOutputSchema


class AgentProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        agent_engine=None,
        prompt_provider=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self._agent_engine = agent_engine
        self._prompt_provider = prompt_provider
        self._context_provider = context_provider
        self._score_provider = score_provider
        self._tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> AgentOutputSchema:
        context = self.fork_context()
        output = self._run(input=input, context=context)
        self._log.debug(f"\U0001f9fb _run_provider called for: {self._config.name if self._config else 'unknown'}")

        response = output.response if hasattr(output, "response") else str(output)
        decision = self._infer_decision(response)
        log_content = self._extract_log(response) or self._default_log(decision)

        snapshot_id = None
        file_name = input.get("before") or input.get("file_path") or (self._config.config or {}).get("before")

        if file_name and (code_block := self._extract_code(response)):
            before_path = Path(file_name)
            try:
                relative_path = before_path.relative_to(Path.cwd())
            except ValueError:
                relative_path = before_path
            before_path = relative_path

            if before_path.exists():
                before_code = before_path.read_text(encoding="utf-8")
                after_code = code_block

                before_metrics = analyze_code(before_code)
                after_metrics = analyze_code(after_code)
                deltas = compute_deltas(before_metrics, after_metrics)

                ctx = self.fork_context()
                score_result = (
                    self._score_provider.run({"file_path": str(before_path)}, context=ctx)
                    if self._score_provider else None
                )

                metadata = {
                    "system": input.get("system", "unknown"),
                    "agent": self._config.name if self._config else "unknown",
                    "score": score_result.value if score_result else None if not hasattr(score_result, "model_dump") else score_result.model_dump(),
                    "state": str(input.get("state_context", {}).get("state", "unknown")),
                    "decision": decision.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **{f"{k}_before": v for k, v in before_metrics.items()},
                    **{f"{k}_after": v for k, v in after_metrics.items()},
                    **deltas,
                }

                after_code = after_code.rstrip() + "\n\n"

                after_code = append_agent_note(
                    file_content=after_code,
                    system=self._called_by_type,
                    agent_name=self._config.name if self._config else "unknown",
                    note=log_content
                )

                snapshot_id = SnapshotWriter().write_snapshot(
                    before=before_code,
                    after=after_code,
                    session_id=self._session_id,
                    metadata=metadata
                )
                with Session(bind=self._engine) as session:
                    entry = SnapshotMetrics(
                        session_id=self._session_id,
                        file_log_id=self._file_log_id,
                        snapshot_id=snapshot_id,
                        system=self._called_by_type,
                        agent=self._config.name,
                        score=metadata.get("score"),
                        state=metadata.get("state"),
                        decision=DECISION_TYPE(metadata.get("decision", "unknown")),
                        timestamp=datetime.fromisoformat(metadata["timestamp"]),
                        **{
                            k: metadata.get(k)
                            for k in SnapshotMetrics.__table__.columns.keys()
                            if k.endswith("_before") or k.endswith("_after") or k.endswith("_delta")
                        }
                    )
                    session.add(entry)
                    session.commit()
                self._snapshot_id = snapshot_id
                self._log.debug(f"\U0001f4e6 Snapshot written to: {snapshot_id}")
            else:
                self._log.warning(f"❌ Snapshot skipped: file does not exist → {before_path}")

        # Always log conversation
        self.logger.write(LOG_TYPE.AGENT_CONVERSATION, AgentConversationLogSchema(
            session_id=self._session_id,
            file_log_id=self._file_log_id,
            system=input.get("system", "unknown"),
            agent_type=self._config.agent_type if hasattr(self._config, "agent_type") else AGENT.BASIC,
            agent_provider_config_id=self._config.id if self._config else -1,
            content=log_content,
            timestamp=datetime.now(timezone.utc),
        ))
        self._log.debug("✅ AGENT_CONVERSATION log write complete")

        return output

    def _infer_decision(self, text: str) -> DECISION_TYPE:
        if "[AGENT_DECISION]accept" in text:
            return DECISION_TYPE.ACCEPTED
        if "[AGENT_DECISION]reject" in text:
            return DECISION_TYPE.REJECTED
        return DECISION_TYPE.UNKNOWN

    def _extract_log(self, text: str) -> str | None:
        return self._extract_block(text, "[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")

    def _default_log(self, decision: DECISION_TYPE) -> str:
        return f"No conversation log entry found. Agent decision was: {decision.value}."

    def _extract_code(self, text: str) -> str | None:
        return self._extract_block(text, "[CODE]", "[/CODE]")

    def _extract_block(self, text: str, start_tag: str, end_tag: str) -> str | None:
        import re
        pattern = re.compile(re.escape(start_tag) + r"(.*?)" + re.escape(end_tag), re.DOTALL)
        match = pattern.search(text)
        return match.group(1).strip() if match else None

    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        raise NotImplementedError
