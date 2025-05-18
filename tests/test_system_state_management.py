import pytest
from importlib import import_module
from app.factories.logging_provider import LoggingProvider
from app.utilities import db
from app.utilities.schema import initialize_database
from app.factories.system_manager import SystemManagerFactory


def _load_extensions() -> None:
    import_module("app.extensions.system_managers")
    import_module("app.extensions.state_managers")
    import_module("app.extensions.agents")
    import_module("app.extensions.prompt_generators")
    import_module("app.extensions.context_providers")
    import_module("app.extensions.tool_providers")
    import_module("app.extensions.scoring_models")


@pytest.mark.usefixtures("tmp_path")
def test_system_fsm_transitions(tmp_path):
    # ✅ Reset singleton to avoid reusing a closed conn
    LoggingProvider._instance = None

    # ✅ Set writable temp DB path
    from app.utilities import db

    db._CONN = None  # 🔥 Force rebind of the database
    db.DB_PATH = tmp_path / "codecritic.sqlite3"
    initialize_database(reset=True)
    _load_extensions()

    logger = LoggingProvider(db_path=db.DB_PATH, output_path=tmp_path / "logs.jsonl")
    manager = SystemManagerFactory.create("system")
    manager.logger = logger  # Optional: ensure logger is consistent

    manager.run()

    expected = [
        "generate",
        "discriminate",
        "mediate",
        "patch",
        "evaluate",
        "end",
    ]
    assert [log.to_state.value for log in manager.transition_logs] == expected
