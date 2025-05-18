from importlib import import_module
from app.abstract_classes.experiment import Experiment
from app.factories.experiment_config_provider import ExperimentConfigProvider
from app.factories.logging_provider import LoggingProvider
from app.utilities import db
from app.utilities.schema import initialize_database
from tests.test_bootstrap import load_all_extensions


def test_end_to_end_experiment(tmp_path):
    # 1) Reset global DB connection and point at a fresh temp file
    db._CONN = None
    db.DB_PATH = tmp_path / "codecritic.sqlite3"

    # 2) Initialize the schema in the writable location
    initialize_database(reset=True)

    # 3) Load all extension registries
    load_all_extensions()

    # 4) Reset LoggingProvider singleton so it re-opens against our temp DB
    LoggingProvider._instance = None

    # 5) Instantiate the logger
    logger = LoggingProvider(
        db_path=db.DB_PATH,
        output_path=tmp_path / "demo_logs.jsonl",
    )

    # 6) Register experiment config and run
    config = {"system_manager_id": "system", "scoring_model_id": "basic"}
    ExperimentConfigProvider.register(1, config)

    exp = Experiment(config_id=1, logger=logger)
    metrics = exp.run()

    # 7) Verify output
    assert "functional_correctness" in metrics
