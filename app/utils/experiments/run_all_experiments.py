# app/utils/experiments/run_all_experiments.py

from pathlib import Path
import json
from importlib import import_module
from app.schemas.experiment_config_schemas import ExperimentConfig

SYSTEM_RUNNER_MAP = {
    "Preprocessing": "app.systems.preprocessing.preprocessor_trainer.PreprocessingTrainer",
    # Future mappings here, e.g.:
    # "Training": "app.systems.training.training_trainer.TrainingTrainer",
}

def run_all_experiments(base_dir: Path):
    """
    Scans all experiment config files under `base_dir` and launches the correct trainer dynamically.
    """
    config_paths = list(base_dir.rglob("experiment_config.json"))

    for path in config_paths:
        with path.open("r", encoding="utf-8") as f:
            config_data = json.load(f)
            config = ExperimentConfig(**config_data)

        experiment_root = path.parent.parent
        input_dir = experiment_root / "inputs"
        log_dir = experiment_root / "logs"
        snapshot_dir = experiment_root / "snapshots"

        trainer_path = SYSTEM_RUNNER_MAP.get(config.system.value)
        if not trainer_path:
            print(f"⚠️ No trainer registered for system: {config.system.value}")
            continue

        module_path, class_name = trainer_path.rsplit(".", 1)
        trainer_class = getattr(import_module(module_path), class_name)

        for input_file in input_dir.glob("*.py"):
            trainer = trainer_class(
                input_path=input_file,
                experiment_path=experiment_root,
                config=config,
                log_dir=log_dir,
                snapshot_dir=snapshot_dir
            )
            trainer.run()
