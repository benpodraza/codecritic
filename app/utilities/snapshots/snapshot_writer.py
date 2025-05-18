from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.enums.agent_enums import AgentRole


class SnapshotWriter:
    """Write before/after file snapshots for experiment traceability."""

    def __init__(self, root: str | Path = "experiments/artifacts/snapshots") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_snapshot(
        self,
        *,
        experiment_id: str,
        round: int,
        file_path: str | Path,
        before: str,
        after: str,
        symbol: str,
        agent_role: AgentRole,
    ) -> None:
        if before == after:
            return
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        dir_path = self.root / experiment_id / str(round)
        dir_path.mkdir(parents=True, exist_ok=True)
        base = Path(file_path).name
        before_file = dir_path / f"{base}.{ts}.before"
        after_file = dir_path / f"{base}.{ts}.after"
        meta_file = dir_path / f"{base}.{ts}.meta"
        before_file.write_text(before, encoding="utf-8")
        after_file.write_text(after, encoding="utf-8")
        meta_file.write_text(
            f"symbol:{symbol}\nrole:{agent_role.value}\nexperiment:{experiment_id}\ntimestamp:{ts}\n",
            encoding="utf-8",
        )
