import subprocess
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.factories.agent import AgentFactory
from app.enums.agent_enums import AgentRole
from app.factories.logging_provider import ConversationLog
from app.utilities.snapshots.snapshot_writer import SnapshotWriter


class PatchAgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")
        import_module("app.extensions.tool_providers")

    def _stub(self):
        proc = subprocess.CompletedProcess(["tool"], 0)
        stub = MagicMock()
        stub.run.return_value = proc
        return stub

    @patch("app.extensions.agents.patch_agent.SnapshotWriter.write_snapshot")
    @patch("app.extensions.agents.patch_agent.LoggingProvider.log_code_quality")
    @patch("app.extensions.agents.patch_agent.LoggingProvider.log_error")
    @patch("app.extensions.agents.patch_agent.LoggingProvider.log_conversation")
    @patch("app.extensions.agents.patch_agent.ToolProviderFactory.create")
    @patch("app.extensions.agents.patch_agent._analyze_radon", return_value=(1.0, 90.0))
    def test_patch_success(
        self, mock_radon, mock_create, log_conv, log_err, log_q, snap
    ):
        black = self._stub()
        ruff = self._stub()
        mypy = self._stub()
        mock_create.side_effect = [black, ruff, mypy]

        tmp = Path("patch_success.py")
        tmp.write_text("x = 1\n")
        try:
            conv = ConversationLog(
                experiment_id="exp",
                round=0,
                agent_role=AgentRole.MEDIATOR,
                target=str(tmp),
                content='[{"op":"replace","from":"1","to":"2"}, {"op":"append","text":"\\n# done"}]',
                originating_agent="mediator",
                intervention=True,
            )
            agent = AgentFactory.create(
                "patch", target=str(tmp), snapshot_writer=SnapshotWriter(root="snap")
            )
            agent.run(recommendations=[conv])
            self.assertEqual(tmp.read_text(), "x = 2\n\n# done")
            self.assertEqual(len(agent.conversation_logs), 1)
            self.assertEqual(len(agent.quality_logs), 1)
            self.assertEqual(agent.error_logs, [])
            log_conv.assert_called_once()
            log_q.assert_called_once()
            log_err.assert_not_called()
            snap.assert_called_once()
        finally:
            tmp.unlink(missing_ok=True)

    @patch("app.extensions.agents.patch_agent.SnapshotWriter.write_snapshot")
    @patch("app.extensions.agents.patch_agent.LoggingProvider.log_error")
    @patch("app.extensions.agents.patch_agent.LoggingProvider.log_conversation")
    @patch("app.extensions.agents.patch_agent.ToolProviderFactory.create")
    def test_patch_conflict(self, mock_create, log_conv, log_err, snap):
        black = self._stub()
        ruff = self._stub()
        mypy = self._stub()
        mock_create.side_effect = [black, ruff, mypy]

        tmp = Path("patch_fail.py")
        tmp.write_text("x = 1\n")
        try:
            conv = ConversationLog(
                experiment_id="exp",
                round=0,
                agent_role=AgentRole.MEDIATOR,
                target=str(tmp),
                content='[{"op":"replace","from":"missing","to":"0"}]',
                originating_agent="mediator",
                intervention=True,
            )
            agent = AgentFactory.create(
                "patch", target=str(tmp), snapshot_writer=SnapshotWriter(root="snap")
            )
            agent.run(recommendations=[conv])
            self.assertEqual(tmp.read_text(), "x = 1\n")
            self.assertEqual(len(agent.error_logs), 1)
            log_err.assert_called()
            log_conv.assert_called_once()
            snap.assert_called_once()
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
