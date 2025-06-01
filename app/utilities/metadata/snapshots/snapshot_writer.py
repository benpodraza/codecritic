import json
import uuid
import sys
from datetime import datetime, timezone
from pathlib import Path


class SnapshotWriter:
    def __init__(self, root: str | Path = None) -> None:
        if root is None:
            if getattr(sys, 'ps1', False) or 'ipykernel' in sys.modules:
                # 🧪 Interactive mode or notebook
                self.root = Path.cwd() / "experiments" / "snapshots"
            else:
                PROJECT_ROOT = Path(__file__).resolve().parents[4]
                self.root = PROJECT_ROOT / "experiments" / "snapshots"
        else:
            self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_snapshot(self, *, before: str, after: str, session_id: str, metadata: dict | None = None) -> str:

        if before == after:
            print("⛔ Snapshot skipped: before == after")
            return ""

        session_root = self.root / session_id
        session_root.mkdir(parents=True, exist_ok=True)

        snapshot_id = str(uuid.uuid4())
        (session_root / f"{snapshot_id}.before").write_text(before, encoding="utf-8")
        (session_root / f"{snapshot_id}.after").write_text(after, encoding="utf-8")

        if metadata:
            metadata.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
            (session_root / f"{snapshot_id}.meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return snapshot_id
