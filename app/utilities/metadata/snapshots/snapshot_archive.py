import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
from dataclasses import dataclass

from app.db.models import SnapshotMetrics
from app.db.schemas import DECISION_TYPE, SnapshotContext
from app.enums.logging_enums import RunContext
from app.utilities.metadata.snapshots.analyze_code_metrics import analyze_code, compute_deltas
from app.utilities.metadata.footer.code_annnotation_utils import append_agent_note


SNAPSHOT_ROOT = Path(__file__).resolve().parents[4] / "experiments" / "snapshots"


class SnapshotArchive:
    def __init__(self, engine, root: Path | str | None = None) -> None:
        self.root = Path(root) if root else SNAPSHOT_ROOT
        self.root.mkdir(parents=True, exist_ok=True)
        self.engine = engine

    def record(self, *, snapshot: SnapshotContext) -> str:
        if not snapshot.before_path.exists():
            raise FileNotFoundError(f"Cannot snapshot non-existent file: {snapshot.before_path}")

        before_content = snapshot.before_path.read_text(encoding="utf-8")

        if not snapshot.after_content or not snapshot.decision or not snapshot.log:
            raise ValueError("Extraction failed: missing content or decision or log entry")

        after_content = snapshot.after_content.rstrip() + "\n\n"
        after_content = append_agent_note(after_content, system=snapshot.system, agent_name=snapshot.agent_name, note=snapshot.log)

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

        session_root = self.root / str(context.session_id)
        session_root.mkdir(parents=True, exist_ok=True)
        snapshot_id = str(uuid.uuid4())

        (session_root / f"{snapshot_id}.before").write_text(before_content, encoding="utf-8")
        (session_root / f"{snapshot_id}.after").write_text(after_content, encoding="utf-8")
        (session_root / f"{snapshot_id}.meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

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
                }
            )
            session.add(entry)
            session.commit()

        return snapshot_id

    def read_latest(self, session_id: str) -> dict | None:
        session_root = self.root / str(session_id)
        if not session_root.exists():
            return None

        snapshots = sorted(session_root.glob("*.before"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not snapshots:
            return None

        latest_id = snapshots[0].stem
        before_path = session_root / f"{latest_id}.before"
        after_path = session_root / f"{latest_id}.after"

        return {
            "before": before_path.read_text(encoding="utf-8"),
            "after": after_path.read_text(encoding="utf-8"),
            "before_path": str(before_path),
            "after_path": str(after_path),
        }
