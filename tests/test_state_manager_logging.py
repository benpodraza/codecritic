import sqlite3
from importlib import import_module

from app.extensions.state_managers.state_manager import StateManager
from app.enums.system_enums import SystemState, StateTransitionReason
from app.factories.logging_provider import LoggingProvider


def test_state_manager_logging():
    import_module("app.extensions.state_managers")
    conn = sqlite3.connect(":memory:")
    logger = LoggingProvider(connection=conn)
    manager = StateManager(logger=logger)

    manager.transition_state(
        experiment_id="exp",
        round=1,
        from_state=SystemState.START,
        to_state=SystemState.GENERATE,
        reason=StateTransitionReason.FIRST_ROUND,
    )
    manager.run_state(
        experiment_id="exp",
        system="system",
        round=1,
        state=SystemState.GENERATE,
        action="run",
        score=1.0,
        details="",
    )

    cur = conn.cursor()
    trans = cur.execute(
        "SELECT experiment_id, round, from_state, to_state, reason FROM state_transition_log"
    ).fetchone()
    assert trans == (
        "exp",
        1,
        SystemState.START.value,
        SystemState.GENERATE.value,
        StateTransitionReason.FIRST_ROUND.value,
    )

    state = cur.execute(
        "SELECT experiment_id, system, round, state, action, score, details FROM state_log"
    ).fetchone()
    assert state == (
        "exp",
        "system",
        1,
        SystemState.GENERATE.value,
        "run",
        1.0,
        "",
    )
