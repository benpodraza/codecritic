# app/utils/experiments/path_utils.py

from pathlib import Path
from typing import Tuple


def get_experiment_paths(experiment_root: Path, experiment_id: str, run_id: str) -> dict:
    base_path = experiment_root / experiment_id / run_id
    log_dir = base_path / "logs"
    return {
        "log_dir": log_dir,
        "snapshot_dir": base_path / "snapshots",
        "config_path": base_path / "config" / "experiment_config.json",
        "review_dir": base_path / "review",
        "summary_yaml": experiment_root / experiment_id / "final_summary.yaml",
    }
