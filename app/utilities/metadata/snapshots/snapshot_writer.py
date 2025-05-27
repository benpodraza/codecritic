import uuid
from pathlib import Path

class SnapshotWriter:
    def __init__(self, root: str | Path = None) -> None:
        if root is None:
            PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
            self.root = PROJECT_ROOT / "experiments" / "snapshots"
        else:
            self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_snapshot(self, *, before: str, after: str, session_id: str) -> str:
        if before == after:
            return ""

        session_root = self.root / session_id
        session_root.mkdir(parents=True, exist_ok=True)

        snapshot_id = str(uuid.uuid4())
        (session_root / f"{snapshot_id}.before").write_text(before, encoding="utf-8")
        (session_root / f"{snapshot_id}.after").write_text(after, encoding="utf-8")

        return snapshot_id
