from __future__ import annotations
from abc import abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from app.providers.base_provider import BaseProvider
from app.utilities.metadata.snapshots.analyze_code_metrics import analyze_code, compute_deltas
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter
from app.utilities.metadata.footer.code_annnotation_utils import (
    split_code_and_notes,
    append_agent_note
)
from app.db.models import SnapshotMetrics

class AgentEngineProviderBase(BaseProvider):
    """Base class for agent engines that return raw LLM output and manage snapshots."""

    def __init__(
        self,
        config=None,
        engine=None,
        prompt_provider=None,
        context_provider=None,
        score_provider=None,
        tool_providers=None,
    ):
        super().__init__(config=config, engine=engine)
        self.prompt_provider = prompt_provider
        self.context_provider = context_provider
        self.score_provider = score_provider
        self.tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> str:
        file_path = input.get("before") or input.get("file_path") or (self.config.config or {}).get("before")
        session_id = input.get("session_id", "")
        system = input.get("system", "unknown")

        before_code = ""
        prior_notes = ""
        if file_path:
            path = Path(file_path).resolve()
            if path.exists():
                full_code = path.read_text(encoding="utf-8")
                before_code, prior_notes = split_code_and_notes(full_code)
        # Initialize output to avoid UnboundLocalError
        output = None

        try:
            # === Call the LLM ===
            output = self._run(input)

            # === Extract code and log blocks ===
            code_block = self._extract_block(output, "[CODE]", "[/CODE]")
            log_block = self._extract_block(output, "[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")
            # If no code change, skip snapshot but still log the decision
            if not code_block or not before_code or code_block == before_code:
                # Still add the discriminator's decision to the log if no change is made
                agent_decision = "[AGENT_DECISION]accept" if "[AGENT_DECISION]accept" in output else "[AGENT_DECISION]reject"
                log_message = f"Code passed all stability checks. Discriminator decision: {agent_decision}"
                self._log.debug(log_message)  # Log the decision
                return output

            # Build after_code: reattach prior notes, append new log if present
            after_code = code_block.rstrip()
            if prior_notes:
                after_code += f"\n\n{prior_notes}"
            if log_block:
                after_code = append_agent_note(
                    after_code,
                    system=system,
                    agent_name=self.config.name,
                    note=log_block,
                )

            # Compute metrics and deltas
            before_metrics = analyze_code(before_code)
            after_metrics = analyze_code(after_code)
            deltas = compute_deltas(before_metrics, after_metrics)

            # Build metadata
            metadata = {
                "system": system,
                "agent": self.config.name,
                "score": None,
                "state": input.get("state_context", {}).get("state", "unknown"),
                "decision": "accept" if "[AGENT_DECISION]accept" in output else (
                    "reject" if "[AGENT_DECISION]reject" in output else "unknown"
                ),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **{f"{k}_before": v for k, v in before_metrics.items()},
                **{f"{k}_after": v for k, v in after_metrics.items()},
                **deltas,
            }

            # Write snapshot to disk and DB
            snapshot_path = SnapshotWriter().write_snapshot(
                before=before_code,
                after=after_code,
                session_id=session_id,
                metadata=metadata,
            )
            with Session(bind=self._engine) as session:
                entry = SnapshotMetrics(
                    session_id=session_id,
                    snapshot_id=snapshot_path,
                    system=system,
                    agent=self.config.name,
                    score=None,
                    state=metadata["state"],
                    decision=metadata["decision"],
                    timestamp=datetime.fromisoformat(metadata["timestamp"]),
                    **{
                        k: metadata.get(k)
                        for k in SnapshotMetrics.__table__.columns.keys()
                        if k.endswith("_before") or k.endswith("_after") or k.endswith("_delta")
                    },
                )
                session.add(entry)
                session.commit()
            self._log.debug(f"📦 Snapshot written: {snapshot_path}")

        except Exception as exc:
            # Log the error
            self._log.error(f"Error during agent run: {exc}")

        return output
    
    def _extract_block(self, text: str, start_tag: str, end_tag: str) -> str | None:
        """
        Extracts the block of text between the specified start and end tags.
        If the block is not found, it returns None.

        :param text: The text to search within.
        :param start_tag: The tag indicating the start of the block.
        :param end_tag: The tag indicating the end of the block.
        :return: Extracted text block or None if not found.
        """
        start = text.find(start_tag)
        end = text.find(end_tag)
        if start != -1 and end != -1 and start < end:
            return text[start + len(start_tag):end].strip()
        return None


    @abstractmethod
    def _run(self, input: dict) -> str:
        """Implement this to call the actual LLM engine."""
        raise NotImplementedError