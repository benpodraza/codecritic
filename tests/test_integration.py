from importlib import import_module
import sqlite3

from app.abstract_classes.experiment import Experiment
from app.factories.experiment_config_provider import ExperimentConfigProvider
from app.factories.logging_provider import LoggingProvider
from app.utilities.metrics import EVALUATION_METRICS
from app.utilities import db


def _load_extensions() -> None:
    import_module("app.extensions.agents")
    import_module("app.extensions.tool_providers")
    import_module("app.extensions.context_providers")
    import_module("app.extensions.prompt_generators")
    import_module("app.extensions.state_managers")
    import_module("app.extensions.system_managers")
    import_module("app.extensions.scoring_models")


from app.utilities import db
from app.utilities.schema import initialize_database


def test_end_to_end_experiment(tmp_path):
    # Override DB path and initialize
    db.DB_PATH = tmp_path / "codecritic.sqlite3"
    initialize_database(reset=True)

    # Load registries from database AFTER init
    _load_extensions()

    # Set up logging
    log_path = tmp_path / "demo_logs.jsonl"
    logger = LoggingProvider(db_path=db.DB_PATH, output_path=log_path)

    # Register config and run
    config = {"system_manager_id": "system", "scoring_model_id": "basic"}
    ExperimentConfigProvider.register(1, config)
    exp = Experiment(config_id=1, logger=logger)

    metrics = exp.run()

    assert "functional_correctness" in metrics
