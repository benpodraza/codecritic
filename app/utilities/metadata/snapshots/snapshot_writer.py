import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_ROOT = Path(__file__).resolve().parents[4] / "experiments" / "snapshots"


class SnapshotWriter:
    def __init__(self, root: Path | str | None = None) -> None:
        self.root = Path(root) if root else SNAPSHOT_ROOT
        self.root.mkdir(parents=True, exist_ok=True)

    def write_snapshot(
        self, *, before: str, after: str, session_id: str, metadata: dict | None = None
    ) -> str:

        if before == after:
            return ""

        session_root = self.root / session_id
        session_root.mkdir(parents=True, exist_ok=True)

        snapshot_id = str(uuid.uuid4())
        (session_root / f"{snapshot_id}.before").write_text(before, encoding="utf-8")
        (session_root / f"{snapshot_id}.after").write_text(after, encoding="utf-8")

        if metadata:
            metadata.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
            meta_path = session_root / f"{snapshot_id}.meta.json"
            meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return snapshot_id
