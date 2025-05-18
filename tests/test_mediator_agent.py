import unittest
from importlib import import_module
from unittest.mock import patch

from app.factories.agent import AgentFactory


class MediatorAgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")

    @patch("app.extensions.agents.mediator_agent.SnapshotWriter.write_snapshot")
    @patch("app.extensions.agents.mediator_agent.LoggingProvider.log_conversation")
    @patch("app.extensions.agents.mediator_agent.LoggingProvider.log_error")
    def test_mediator_with_discrepancy(self, log_error, log_conv, snap):
        agent = AgentFactory.create("mediator", target="demo.py")
        agent.run(
            generator_output="x=1",
            evaluation_metrics={"lint_errors": 1, "maintainability_index": 60},
        )
        self.assertEqual(len(agent.conversation_logs), 1)
        self.assertTrue(agent.conversation_logs[0].intervention)
        self.assertIn("Resolve lint errors", agent.conversation_logs[0].content)
        snap.assert_called_once()
        log_conv.assert_called_once()
        log_error.assert_not_called()

    @patch("app.extensions.agents.mediator_agent.LoggingProvider.log_conversation")
    @patch("app.extensions.agents.mediator_agent.LoggingProvider.log_error")
    def test_mediator_no_discrepancy(self, log_error, log_conv):
        agent = AgentFactory.create("mediator", target="demo.py")
        agent.run(
            generator_output="x=1",
            evaluation_metrics={"lint_errors": 0, "maintainability_index": 90},
        )
        self.assertEqual(len(agent.conversation_logs), 1)
        self.assertFalse(agent.conversation_logs[0].intervention)
        self.assertEqual(agent.conversation_logs[0].content, "")
        log_conv.assert_called_once()
        log_error.assert_not_called()

    @patch("app.extensions.agents.mediator_agent.LoggingProvider.log_conversation")
    @patch("app.extensions.agents.mediator_agent.LoggingProvider.log_error")
    def test_mediator_missing_metrics(self, log_error, log_conv):
        agent = AgentFactory.create("mediator", target="demo.py")
        agent.run(generator_output="x=1", evaluation_metrics=None)
        self.assertEqual(len(agent.error_logs), 1)
        log_conv.assert_not_called()
        log_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
