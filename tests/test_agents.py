import unittest
from importlib import import_module
from pathlib import Path
import shutil

from app.utilities.snapshots.snapshot_writer import SnapshotWriter

from app.factories.agent import AgentFactory


class AgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")
        import_module("app.extensions.tool_providers")

    def test_generator_agent(self):
        tmp = Path("temp_gen.py")
        tmp.write_text("x=1")
        snap_dir = Path("snap_test")
        try:
            writer = SnapshotWriter(root=snap_dir)
            agent = AgentFactory.create(
                "generator", target=str(tmp), snapshot_writer=writer
            )
            agent.run()
            self.assertEqual(tmp.read_text(), "x = 1\n")
            self.assertIsNotNone(agent.prompt_logs[0].stop)
            snaps = list((snap_dir / "exp" / "0").glob("*.before"))
            self.assertTrue(snaps)
        finally:
            tmp.unlink(missing_ok=True)
            shutil.rmtree(snap_dir, ignore_errors=True)

    def test_evaluator_agent(self):
        tmp = Path("temp_eval.py")
        tmp.write_text("x = 1\n")
        try:
            agent = AgentFactory.create("evaluator", target=str(tmp))
            agent.run()
            self.assertEqual(len(agent.quality_logs), 1)
            qlog = agent.quality_logs[0]
            self.assertGreaterEqual(qlog.cyclomatic_complexity, 0.0)
            self.assertIn(qlog.lint_errors, (0, 1))
        finally:
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
