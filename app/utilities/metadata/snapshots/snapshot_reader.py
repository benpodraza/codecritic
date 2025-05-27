import json
from pathlib import Path

def read_latest_snapshot(session_id: str, root="experiments/snapshots"):
    session_root = Path(root) / session_id
    if not session_root.exists():
        return None

    snapshots = sorted(session_root.glob("*.before"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not snapshots:
        return None

    latest_snapshot_id = snapshots[0].stem
    before = (session_root / f"{latest_snapshot_id}.before").read_text(encoding="utf-8")
    after = (session_root / f"{latest_snapshot_id}.after").read_text(encoding="utf-8")

    return {"before": before, "after": after}