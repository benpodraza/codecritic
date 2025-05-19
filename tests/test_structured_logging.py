import sqlite3

from app.factories.logging_provider import LoggingProvider
from app.extensions.context_providers.dummy_context_provider import DummyContextProvider
from app.extensions.tool_providers.dummy_tool_provider import DummyToolProvider
from app.extensions.agents.dummy_agent import DummyAgent
from app.extensions.experiment_provider import ExperimentProvider


def test_structured_logs():
    conn = sqlite3.connect(":memory:")
    logger = LoggingProvider(connection=conn)
    ctx = DummyContextProvider(logger=logger)
    tool = DummyToolProvider(logger=logger)
    agent = DummyAgent(logger=logger)
    exp = ExperimentProvider(
        "demo",
        "demo experiment",
        "test",
        "v1",
        1,
        0.0,
        "engine",
        "eval",
        "1.0",
        logger=logger,
    )
    ctx.get_context(experiment_id="demo", round=0)
    tool.run(experiment_id="demo", round=0)
    agent.run(experiment_id="demo", round=0)
    exp.complete(1.0, True, "done")

    cur = conn.cursor()
    for table in [
        "context_retrieval_log",
        "tool_invocation_log",
        "agent_action_log",
        "system_event_log",
        "experiment_log",
    ]:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count == 1
