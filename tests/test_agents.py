import subprocess
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.factories.agent import AgentFactory
from app.utilities.snapshots.snapshot_writer import SnapshotWriter


class EvaluatorAgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")
        import_module("app.extensions.tool_providers")

    def _make_stub(self, returncode: int = 0, stdout: str = ""):
        proc = subprocess.CompletedProcess(
            ["tool"], returncode, stdout=stdout, stderr=""
        )
        mock = MagicMock()
        mock.run.return_value = proc
        return mock

    @patch("app.extensions.agents.evaluator_agent.ToolProviderFactory.create")
    @patch(
        "app.extensions.agents.evaluator_agent._analyze_radon", return_value=(2.0, 75.0)
    )
    def test_evaluator_success(self, mock_analyze, mock_create):
        radon = self._make_stub()
        ruff = self._make_stub(returncode=1)
        mypy = self._make_stub()
        black = self._make_stub()
        mock_create.side_effect = lambda name: {
            "radon": radon,
            "ruff": ruff,
            "mypy": mypy,
            "black": black,
        }[name]

        tmp = Path("eval_success.py")
        tmp.write_text("x = 1\n")
        try:
            agent = AgentFactory.create(
                "evaluator",
                target=str(tmp),
                snapshot_writer=SnapshotWriter(root="snap_s"),
            )
            agent.run()
            self.assertEqual(len(agent.quality_logs), 1)
            qlog = agent.quality_logs[0]
            self.assertEqual(qlog.cyclomatic_complexity, 2.0)
            self.assertEqual(qlog.maintainability_index, 75.0)
            self.assertEqual(qlog.lint_errors, 1)
            self.assertFalse(list(Path("snap_s/exp/0").glob("*.before")))
        finally:
            tmp.unlink(missing_ok=True)

    @patch("app.extensions.agents.evaluator_agent.ToolProviderFactory.create")
    @patch(
        "app.extensions.agents.evaluator_agent._analyze_radon", return_value=(0.0, 0.0)
    )
    def test_evaluator_radon_failure(self, mock_analyze, mock_create):
        radon = MagicMock()
        radon.run.side_effect = RuntimeError("no radon")
        ruff = self._make_stub()
        mypy = self._make_stub()
        black = self._make_stub()
        mock_create.side_effect = lambda name: {
            "radon": radon,
            "ruff": ruff,
            "mypy": mypy,
            "black": black,
        }[name]

        tmp = Path("eval_fail.py")
        tmp.write_text("x = 1\n")
        try:
            agent = AgentFactory.create("evaluator", target=str(tmp))
            agent.run()
            qlog = agent.quality_logs[0]
            self.assertEqual(qlog.cyclomatic_complexity, 0.0)
            self.assertEqual(qlog.maintainability_index, 0.0)
            self.assertEqual(qlog.lint_errors, 0)
            self.assertGreaterEqual(len(agent.error_logs), 1)
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
