import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.models import SnapshotMetrics
from app.db.schemas import DECISION_TYPE, SnapshotContext
from app.utilities.metadata.snapshots.analyze_code_metrics import analyze_code, compute_deltas
from app.utilities.metadata.footer.code_annnotation_utils import append_agent_note
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE


class SnapshotArchive:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.fm = get_file_manager()

    def record(self, *, snapshot: SnapshotContext) -> str:
        # 🔁 Determine canonical path via file manager
        before_candidate = str(snapshot.before_path)
        try:
            resolved_type = self.fm.resolve_existing_filetype(before_candidate)
            path = self.fm._resolve(resolved_type, before_candidate)
        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot snapshot non‑existent file: {snapshot.before_path}")

        before_content = self.fm.load(resolved_type, path.name)

        if not snapshot.after_content or not snapshot.decision or not snapshot.log:
            raise ValueError("Extraction failed: missing content or decision or log entry")

        after_content = snapshot.after_content.rstrip() + "\n\n"
        after_content = append_agent_note(
            after_content,
            system=snapshot.system,
            agent_name=snapshot.agent_name,
            note=snapshot.log,
        )

        before_metrics = analyze_code(before_content)
        after_metrics = analyze_code(after_content)
        deltas = compute_deltas(before_metrics, after_metrics)

        timestamp = datetime.now(timezone.utc)
        context = snapshot.context

        metadata = {
            "system": snapshot.system,
            "agent": snapshot.agent_name,
            "state": snapshot.state,
            "decision": snapshot.decision,
            "timestamp": timestamp.isoformat(),
            **{f"{k}_before": v for k, v in before_metrics.items()},
            **{f"{k}_after": v for k, v in after_metrics.items()},
            **deltas,
        }

        snapshot_id = str(uuid.uuid4())
        base_filename = f"{context.file_log_id}__{snapshot_id}"

        self.fm.save(FILETYPE.SNAPSHOT, f"{base_filename}.before", before_content)
        self.fm.save(FILETYPE.SNAPSHOT, f"{base_filename}.after", after_content)
        self.fm.save(FILETYPE.SNAPSHOT, f"{base_filename}.meta.json", json.dumps(metadata, indent=2))

        with Session(bind=self.engine) as session:
            entry = SnapshotMetrics(
                session_id=context.session_id,
                file_log_id=context.file_log_id,
                snapshot_id=snapshot_id,
                system=snapshot.system,
                agent=snapshot.agent_name,
                score=None,
                state=snapshot.state,
                decision=DECISION_TYPE(snapshot.decision),
                timestamp=timestamp,
                **{
                    k: metadata.get(k)
                    for k in SnapshotMetrics.__table__.columns.keys()
                    if k.endswith("_before") or k.endswith("_after") or k.endswith("_delta")
                },
            )
            session.add(entry)
            session.commit()

        return snapshot_id

    def read_latest(self, file_log_id: int) -> dict | None:
        with Session(bind=self.engine) as session:
            row = (
                session.query(SnapshotMetrics)
                .filter(SnapshotMetrics.file_log_id == file_log_id)
                .order_by(SnapshotMetrics.timestamp.desc())
                .first()
            )

        if not row:
            return None

        base_filename = f"{file_log_id}__{row.snapshot_id}"
        before_name = f"{base_filename}.before"
        after_name = f"{base_filename}.after"

        if not self.fm.exists(FILETYPE.SNAPSHOT, before_name) or not self.fm.exists(FILETYPE.SNAPSHOT, after_name):
            return None

        before_path = self.fm._resolve(FILETYPE.SNAPSHOT, before_name)
        after_path = self.fm._resolve(FILETYPE.SNAPSHOT, after_name)

        return {
            "before": self.fm.load(FILETYPE.SNAPSHOT, before_name),
            "after": self.fm.load(FILETYPE.SNAPSHOT, after_name),
            "before_path": str(before_path),
            "after_path": str(after_path),
        }
