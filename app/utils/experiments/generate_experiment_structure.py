# app/utils/experiments/generate_experiment_structure.py

import json
from pathlib import Path
from app.schemas.experiment_config_schemas import ExperimentConfig

def generate_experiment_structure(config: ExperimentConfig, base_dir: Path = Path("experiments")) -> Path:
    """
    Creates the folder structure and config file for a new experiment run.
    
    Structure:
    experiments/{system}/{experiment_id}/{run_id}/
        ├── config/
        │   └── experiment_config.json
        ├── inputs/
        ├── outputs/
        ├── logs/
        ├── review/
        └── snapshots/
    """
    root = base_dir / config.system.value / config.experiment_id / config.run_id
    config_dir = root / "config"

    for subdir in ["inputs", "outputs", "logs", "review", "snapshots", "config"]:
        (root / subdir).mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "experiment_config.json"
    with config_path.open("w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print(f"📁 Experiment structure created at: {root}")
    return root
