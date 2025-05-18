import pytest
from importlib import import_module
from app.abstract_classes.experiment import Experiment
from app.factories.experiment_config_provider import ExperimentConfigProvider


def _load_extensions() -> None:
    import_module("app.extensions.system_managers")
    import_module("app.extensions.state_managers")
    import_module("app.extensions.agents")
    import_module("app.extensions.prompt_generators")
    import_module("app.extensions.context_providers")
    import_module("app.extensions.tool_providers")
    import_module("app.extensions.scoring_models")


def test_end_to_end_experiment(tmp_path):
    # ✅ Reset db connection BEFORE importing logging
    from app.utilities import db

    db._CONN = None
    db.DB_PATH = tmp_path / "codecritic.sqlite3"

    from app.utilities.schema import initialize_database

    initialize_database(reset=True)
    _load_extensions()

    # ✅ Now import and reset LoggingProvider
    from app.factories.logging_provider import LoggingProvider

    LoggingProvider._instance = None

    logger = LoggingProvider(db_path=db.DB_PATH, output_path=tmp_path / "logs.jsonl")

    config = {"system_manager_id": "system", "scoring_model_id": "basic"}
    ExperimentConfigProvider.register(1, config)

    exp = Experiment(config_id=1, logger=logger)
    metrics = exp.run()

    assert "functional_correctness" in metrics
