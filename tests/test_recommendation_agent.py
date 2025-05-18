import unittest
from importlib import import_module
from unittest.mock import patch
from pathlib import Path
import tempfile
import json

from app.factories.agent import AgentFactory
from app.enums.agent_enums import AgentRole
from app.factories.logging_provider import (
    ConversationLog,
    CodeQualityLog,
    ScoringLog,
)
from app.enums.scoring_enums import ScoringMetric
from app.utilities.snapshots.snapshot_writer import SnapshotWriter
from app.extensions.context_providers.symbol_graph_provider import SymbolGraphProvider


class RecommendationAgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")

    @patch("app.extensions.agents.recommendation_agent.SnapshotWriter.write_snapshot")
    @patch(
        "app.extensions.agents.recommendation_agent.LoggingProvider.log_recommendation"
    )
    @patch(
        "app.extensions.agents.recommendation_agent.LoggingProvider.log_conversation"
    )
    @patch("app.extensions.agents.recommendation_agent.LoggingProvider.log_error")
    def test_generate_recommendation(self, log_err, log_conv, log_rec, snap):
        conv = ConversationLog(
            experiment_id="exp",
            round=0,
            agent_role=AgentRole.MEDIATOR,
            target="demo.py",
            content="Use list comprehension",
            originating_agent="mediator",
            intervention=True,
        )
        qlog = CodeQualityLog(
            experiment_id="exp",
            round=0,
            symbol="demo.py",
            lines_of_code=10,
            cyclomatic_complexity=12.0,
            maintainability_index=60.0,
            lint_errors=1,
        )
        slog = ScoringLog(
            experiment_id="exp",
            round=0,
            metric=ScoringMetric.LINTING_COMPLIANCE,
            value=0.3,
        )

        agent = AgentFactory.create(
            "recommendation",
            target="demo.py",
            snapshot_writer=SnapshotWriter(root="rec_snap"),
        )
        agent.run(conversation_log=[conv], code_quality_log=[qlog], scoring_log=[slog])

        self.assertEqual(len(agent.recommendation_logs), 1)
        rec = agent.recommendation_logs[0]
        data = json.loads(rec.recommendation)
        actions = {d["action"] for d in data}
        self.assertIn("general", actions)
        log_rec.assert_called_once()
        log_conv.assert_called_once()
        log_err.assert_not_called()
        snap.assert_called_once()

    @patch(
        "app.extensions.agents.recommendation_agent.LoggingProvider.log_recommendation"
    )
    def test_no_recommendation(self, log_rec):
        agent = AgentFactory.create("recommendation", target="demo.py")
        agent.run(conversation_log=[], code_quality_log=[], scoring_log=[])
        self.assertEqual(agent.recommendation_logs, [])
        log_rec.assert_not_called()

    @patch("app.extensions.agents.recommendation_agent.SnapshotWriter.write_snapshot")
    @patch(
        "app.extensions.agents.recommendation_agent.LoggingProvider.log_recommendation"
    )
    @patch(
        "app.extensions.agents.recommendation_agent.LoggingProvider.log_conversation"
    )
    def test_symbol_graph_analysis(self, log_conv, log_rec, snap):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "mod.py"
            src.write_text(
                """import os\n\n"""
                "def used():\n    return os.getcwd()\n\n"
                "def unused():\n    pass\n\n"
                "def a():\n    b()\n\n"
                "def b():\n    a()\n",
                encoding="utf-8",
            )
            provider = SymbolGraphProvider(str(src))
            agent = AgentFactory.create(
                "recommendation",
                target=str(src),
                context_provider=provider,
                snapshot_writer=SnapshotWriter(root="snap"),
            )
            agent.run()

            self.assertEqual(len(agent.recommendation_logs), 1)
            rec = json.loads(agent.recommendation_logs[0].recommendation)
            actions = {d["action"] for d in rec}
            self.assertIn("remove_unused_symbol", actions)
            self.assertIn("refactor_circular_dependency", actions)
            log_rec.assert_called_once()
            log_conv.assert_called_once()
            assert snap.call_count == 2


if __name__ == "__main__":
    unittest.main()
