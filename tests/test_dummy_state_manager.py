import sqlite3
from unittest.mock import MagicMock

from app.extensions.state_managers.dummy_state_manager import DummyStateManager
from app.extensions.context_providers.dummy_context_provider import DummyContextProvider
from app.extensions.agents.dummy_agent import DummyAgent
from app.enums.system_enums import SystemState
from app.factories.logging_provider import LoggingProvider


def test_dummy_state_manager_transition():
    conn = sqlite3.connect(":memory:")
    logger = LoggingProvider(connection=conn)
    context = DummyContextProvider(logger=logger)
    scoring_fn = MagicMock(return_value=1.0)
    agent = DummyAgent(logger=logger)
    agent.run = MagicMock()

    manager = DummyStateManager(
        scoring_function=scoring_fn,
        context_manager=context,
        agent=agent,
        logger=logger,
    )

    manager.transition_state(
        experiment_id="exp",
        round=0,
        from_state=SystemState.START,
        to_state=SystemState.END,
        reason="test",
    )

    assert scoring_fn.called
    assert agent.run.called

    cur = conn.cursor()
    trans = cur.execute(
        "SELECT experiment_id, round, from_state, to_state, reason FROM state_transition_log"
    ).fetchone()
    assert trans == (
        "exp",
        0,
        SystemState.START.value,
        SystemState.END.value,
        "test",
    )
