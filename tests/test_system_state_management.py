from importlib import import_module

from app.factories.system_manager import SystemManagerFactory


def _load_extensions() -> None:
    import_module("app.extensions.system_managers")
    import_module("app.extensions.state_managers")


def test_system_fsm_transitions():
    _load_extensions()
    manager = SystemManagerFactory.create("system")
    manager.run()
    expected = [
        "generate",
        "discriminate",
        "mediate",
        "patchor",
        "recommender",
        "end",
    ]
    assert [log.to_state.value for log in manager.transition_logs] == expected
