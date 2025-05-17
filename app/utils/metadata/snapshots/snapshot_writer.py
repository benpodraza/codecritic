import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from app.schemas.experiment_config_schemas import ExperimentConfig


class RunSnapshotLogger:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        round_num: int,
        symbol: str,
        original_code: str,
        modified_code: str,
        transition: str,
        config: ExperimentConfig,
        score: Optional[dict] = None
    ):
        snapshot_path = self.base_dir / f"round_{round_num}" / symbol
        snapshot_path.mkdir(parents=True, exist_ok=True)

        (snapshot_path / "original.py").write_text(original_code, encoding="utf-8")
        (snapshot_path / "annotated.py").write_text(modified_code, encoding="utf-8")

        metadata = {
            "experiment_id": config.experiment_id,
            "run_id": config.run_id,
            "round": round_num,
            "state": transition,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "score": score or {}
        }
        with (snapshot_path / "metadata.json").open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

