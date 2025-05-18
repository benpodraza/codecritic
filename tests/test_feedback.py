import unittest
from importlib import import_module
from unittest.mock import patch, MagicMock
from pathlib import Path

from app.utilities.feedback import FeedbackRepository
from app.utilities.metadata.logging.log_schemas import FeedbackLog
from app.factories.agent import AgentFactory


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")
        import_module("app.extensions.tool_providers")
        FeedbackRepository.clear()

    def test_repository(self):
        log = FeedbackLog(
            experiment_id="exp", round=0, source="tester", feedback="good"
        )
        FeedbackRepository.add_feedback(log)
        logs = FeedbackRepository.get_feedback("exp")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].feedback, "good")

    @patch("app.extensions.agents.generator_agent.ToolProviderFactory.create")
    @patch("app.extensions.agents.generator_agent.SnapshotWriter.write_snapshot")
    @patch("app.extensions.agents.generator_agent.LoggingProvider.log_feedback")
    def test_agent_accepts_feedback(self, log_fb, snap, mock_create):
        stub = MagicMock()
        stub.run.return_value = MagicMock()
        mock_create.return_value = stub

        tmp = Path("g.py")
        tmp.write_text("x=1\n")
        try:
            agent = AgentFactory.create("generator", target=str(tmp))
            agent.run(feedback=["formatting"])
            log_fb.assert_called()
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
