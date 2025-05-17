import unittest
from importlib import import_module
from pathlib import Path

from app.factories.agent import AgentFactory


class AgentTests(unittest.TestCase):
    def setUp(self):
        import_module("app.extensions.agents")
        import_module("app.extensions.tool_providers")

    def test_generator_agent(self):
        tmp = Path("temp_gen.py")
        tmp.write_text("x=1")
        try:
            agent = AgentFactory.create("generator", target=str(tmp))
            agent.run()
            self.assertEqual(tmp.read_text(), "x = 1\n")
            self.assertIsNotNone(agent.prompt_logs[0].stop)
        finally:
            tmp.unlink(missing_ok=True)

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
