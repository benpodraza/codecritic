from __future__ import annotations
from abc import abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.models import SnapshotMetrics
from app.db.schemas import AgentEngineOutput, SnapshotMetricsSchema
from app.enums.system_enums import SYSTEM_TYPE
from app.enums.agent_enums import AGENT_TYPE
from app.enums.fsm_enums import DECISION_TYPE
from app.enums.logging_enums import LOG_TYPE

from app.providers.base_provider import BaseProvider
from app.utilities.metadata.snapshots.analyze_code_metrics import analyze_code, compute_deltas
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter
from app.utilities.metadata.footer.code_annnotation_utils import (
    split_code_and_notes,
    append_agent_note
)


class AgentEngineProviderBase(BaseProvider):
    """Base class for agent engines that return raw LLM output and manage snapshots."""

    def __init__(
        self,
        config=None,
        prompt_provider=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
        called_by_type=None,
        called_by_id=None,
    ):
        super().__init__(config=config, called_by_type=called_by_type, called_by_id=called_by_id)
        self.prompt_provider = prompt_provider
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> AgentEngineOutput:
        file_path = input.get("before") or input.get("file_path") or (self._config.config or {}).get("before")
        session_id = input.get("session_id", "")
        system = SYSTEM_TYPE(input.get("system", SYSTEM_TYPE.UNKNOWN))
        agent_type = AGENT_TYPE(input.get("agent_type", AGENT_TYPE.UNKNOWN))
        agent_id = input.get("agent_id", -1)

        before_code = ""
        prior_notes = ""
        if file_path:
            path = Path(file_path).resolve()
            if path.exists():
                full_code = path.read_text(encoding="utf-8")
                before_code, prior_notes = split_code_and_notes(full_code)

        response_text = ""
        snapshot_id = None
        summary = None
        token_count = 0

        try:
            raw_output = self._run(input)
            if isinstance(raw_output, AgentEngineOutput):
                response_text = raw_output.response
                token_count = raw_output.token_count
                cost_usd = raw_output.cost_usd
            else:
                response_text = raw_output
                token_count = len(response_text.split())
                cost_usd = token_count * (self._config.cost_per_1k_tokens or 0.0) / 1000

            code_block = self._extract_block(response_text, "[CODE]", "[/CODE]")
            log_block = self._extract_block(response_text, "[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")

            if "[AGENT_DECISION]accept" in response_text:
                decision = DECISION_TYPE.ACCEPT
            elif "[AGENT_DECISION]reject" in response_text:
                decision = DECISION_TYPE.REJECT
            else:
                decision = DECISION_TYPE.UNKNOWN

            def normalize_code(code: str) -> str:
                return "\n".join(line.strip() for line in code.strip().splitlines() if line.strip())

            if not code_block or not before_code or normalize_code(code_block) == normalize_code(before_code):
                self._log.debug("🟡 Generator returned output matching input (normalized)")
                self._log.debug(f"🔍 BEFORE:\n{before_code}")
                self._log.debug(f"🆕 AFTER:\n{code_block}")
                return AgentEngineOutput(
                    response=response_text,
                    token_count=token_count,
                    cost_usd=cost_usd,
                    snapshot_id=None,
                    summary="No change detected (normalized)",
                )

            after_code = code_block.rstrip()
            if prior_notes:
                after_code += f"\n\n{prior_notes}"
            if log_block:
                after_code = append_agent_note(after_code, system=system.value, agent_name=self._config.name, note=log_block)

            before_metrics = analyze_code(before_code)
            after_metrics = analyze_code(after_code)
            deltas = compute_deltas(before_metrics, after_metrics)

            timestamp = datetime.now(timezone.utc)
            metadata = {
                "system": system.value,
                "agent": self._config.name,
                "agent_type": agent_type.value,
                "agent_id": agent_id,
                "score": None,
                "state": str(input.get("state_context", {}).get("state", "unknown")),
                "decision": decision.value,
                "timestamp": timestamp.isoformat(),
                **{f"{k}_before": v for k, v in before_metrics.items()},
                **{f"{k}_after": v for k, v in after_metrics.items()},
                **deltas,
            }

            snapshot_id = SnapshotWriter().write_snapshot(
                before=before_code,
                after=after_code,
                session_id=session_id,
                metadata=metadata,
            )

            with Session(bind=self._engine) as session:
                entry = SnapshotMetrics(
                    session_id=session_id,
                    snapshot_id=snapshot_id,
                    system=system.value,
                    agent=self._config.name,
                    agent_type=agent_type.value,
                    agent_id=agent_id,
                    score=None,
                    state=metadata["state"],
                    decision=decision.value,
                    timestamp=timestamp,
                    **{
                        k: metadata.get(k)
                        for k in SnapshotMetrics.__table__.columns.keys()
                        if k.endswith("_before") or k.endswith("_after") or k.endswith("_delta")
                    },
                )
                session.add(entry)
                session.commit()

            self.logger.write(LOG_TYPE.SNAPSHOT_METRICS, SnapshotMetricsSchema(
                session_id=session_id,
                snapshot_id=snapshot_id,
                system=system,
                agent=self._config.name,
                agent_type=agent_type,
                agent_id=agent_id,
                score=None,
                state=metadata["state"],
                decision=decision,
                timestamp=timestamp,
                line_count_before=metadata["line_count_before"],
                line_count_after=metadata["line_count_after"],
                function_count_before=metadata["function_count_before"],
                function_count_after=metadata["function_count_after"],
                symbol_count_before=metadata["symbol_count_before"],
                symbol_count_after=metadata["symbol_count_after"],
                branch_count_before=metadata["branch_count_before"],
                branch_count_after=metadata["branch_count_after"],
                comment_count_before=metadata["comment_count_before"],
                comment_count_after=metadata["comment_count_after"],
                line_count_delta=metadata["line_count_delta"],
                function_count_delta=metadata["function_count_delta"],
                symbol_count_delta=metadata["symbol_count_delta"],
                branch_count_delta=metadata["branch_count_delta"],
                comment_count_delta=metadata["comment_count_delta"],
            ))

            self._log.debug(f"📦 Snapshot written: {snapshot_id}")
            summary = log_block or "Snapshot successfully written"

        except Exception as exc:
            self._log.error(f"❌ Error during agent run: {exc}")
            summary = f"Error: {str(exc)}"
            cost_usd = 0.0

        return AgentEngineOutput(
            response=response_text,
            token_count=token_count,
            cost_usd=cost_usd,
            snapshot_id=snapshot_id,
            summary=summary,
        )

    def _extract_block(self, text: str, start_tag: str, end_tag: str) -> str | None:
        start = text.find(start_tag)
        end = text.find(end_tag)
        if start != -1 and end != -1 and start < end:
            return text[start + len(start_tag):end].strip()
        return None

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
