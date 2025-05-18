import unittest
from importlib import import_module
from unittest.mock import patch

from app.factories.agent import AgentFactory
from app.enums.agent_enums import AgentRole
from app.factories.logging_provider import (
    ConversationLog,
    CodeQualityLog,
    ScoringLog,
)
from app.enums.scoring_enums import ScoringMetric
from app.utilities.snapshots.snapshot_writer import SnapshotWriter


class RecommendationAgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")

    @patch("app.extensions.agents.recommendation_agent.SnapshotWriter.write_snapshot")
    @patch(
        "app.extensions.agents.recommendation_agent.LoggingProvider.log_recommendation"
    )
    @patch("app.extensions.agents.recommendation_agent.LoggingProvider.log_error")
    def test_generate_recommendation(self, log_err, log_rec, snap):
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
        self.assertIn("Fix lint errors", rec.recommendation)
        self.assertIn("Improve score", rec.recommendation)
        log_rec.assert_called_once()
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


if __name__ == "__main__":
    unittest.main()
