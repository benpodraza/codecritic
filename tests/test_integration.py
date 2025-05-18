from app.abstract_classes.experiment import Experiment
from app.factories.experiment_config_provider import ExperimentConfigProvider
from app.factories.logging_provider import LoggingProvider
from app.utilities import db
from app.utilities.schema import initialize_database
from tests.test_bootstrap import load_all_extensions

# Reset singleton to avoid stale connections
LoggingProvider._instance = None


def test_end_to_end_experiment(tmp_path):
    from app.utilities import db

    db._CONN = None  # 🔥 Force rebind of the database
    db.DB_PATH = tmp_path / "codecritic.sqlite3"
    initialize_database(reset=True)
    load_all_extensions()

    logger = LoggingProvider(db_path=db.DB_PATH, output_path=tmp_path / "logs.jsonl")

    config = {"system_manager_id": "system", "scoring_model_id": "basic"}
    ExperimentConfigProvider.register(1, config)

    exp = Experiment(config_id=1, logger=logger)
    metrics = exp.run()

    assert "functional_correctness" in metrics
