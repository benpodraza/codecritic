from pathlib import Path

SNAPSHOT_ROOT = Path(__file__).resolve().parents[4] / "experiments" / "snapshots"

def read_latest_snapshot(session_id: str, root: Path | str | None = None):
    session_root = Path(root) if root else SNAPSHOT_ROOT
    session_root = session_root / str(session_id)
    
    if not session_root.exists():
        return None

    snapshots = sorted(session_root.glob("*.before"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not snapshots:
        return None

    latest_snapshot_id = snapshots[0].stem
    before_path = session_root / f"{latest_snapshot_id}.before"
    after_path = session_root / f"{latest_snapshot_id}.after"

    return {
        "before": before_path.read_text(encoding="utf-8"),
        "after": after_path.read_text(encoding="utf-8"),
        "before_path": str(before_path),
        "after_path": str(after_path)
    }

