import uuid
from pathlib import Path

class SnapshotWriter:
    """Write before/after file snapshots for experiment traceability."""

    def __init__(self, root: str | Path = "experiments/snapshots") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_snapshot(
        self,
        *,
        before: str,
        after: str,
    ) -> str:
        if before == after:
            return ""

        snapshot_id = str(uuid.uuid4())
        self.root.mkdir(parents=True, exist_ok=True)

        before_file = self.root / f"{snapshot_id}.before"
        before_file.write_text(before, encoding="utf-8")

        after_file = self.root / f"{snapshot_id}.after"        
        after_file.write_text(after, encoding="utf-8")

        return snapshot_id
