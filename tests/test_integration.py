from importlib import import_module
import sqlite3

from app.abstract_classes.experiment import Experiment
from app.factories.experiment_config_provider import ExperimentConfigProvider
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


def test_end_to_end_experiment(tmp_path):
    _load_extensions()
    config = {"system_manager_id": "system", "scoring_model_id": "basic"}
    ExperimentConfigProvider.register(1, config)

    if db.DB_PATH.exists():
        db.DB_PATH.unlink()

    exp = Experiment(config_id=1)
    metrics = exp.run()

    conn = sqlite3.connect(db.DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM state_log")
    assert cur.fetchone()[0] > 0
    cur.execute("SELECT COUNT(*) FROM prompt_log")
    assert cur.fetchone()[0] > 0
    cur.execute("SELECT COUNT(*) FROM scoring_log")
    assert cur.fetchone()[0] > 0
    conn.close()

    assert set(metrics.keys()) == set(EVALUATION_METRICS)
