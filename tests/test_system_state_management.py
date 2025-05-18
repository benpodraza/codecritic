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
    # 1) Reset the global SQLite connection, then point DB_PATH at tmp_path.
    from app.utilities import db

    db._CONN = None
    db.DB_PATH = tmp_path / "codecritic.sqlite3"

    # 2) Now initialize the schema in that fresh, writable location.
    from app.utilities.schema import initialize_database

    initialize_database(reset=True)

    # 3) Load all extension registries.
    _load_extensions()

    # 4) Import & reset the LoggingProvider singleton,
    #    so it too will reopen against the new db.
    from app.factories.logging_provider import LoggingProvider

    LoggingProvider._instance = None

    # 5) Instantiate your logger (its .conn comes from get_connection()).
    logger = LoggingProvider(
        db_path=db.DB_PATH,
        output_path=tmp_path / "demo_logs.jsonl",
    )

    # 6) Register and run the experiment.
    config = {"system_manager_id": "system", "scoring_model_id": "basic"}
    ExperimentConfigProvider.register(1, config)

    exp = Experiment(config_id=1, logger=logger)
    metrics = exp.run()

    # 7) Verify something basic came back.
    assert "functional_correctness" in metrics
