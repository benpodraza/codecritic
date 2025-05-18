import sqlite3
from pathlib import Path
import unittest

from app.visualization.dashboard import (
    load_logs,
    build_state_transition_sankey,
    build_scoring_line_plot,
    build_recommendation_bar_plot,
)


class DashboardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db_path = Path("test_logs.sqlite3")
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE state_transition_log (experiment_id TEXT, round INTEGER, from_state TEXT, to_state TEXT, reason TEXT, timestamp TEXT)"
        )
        cur.execute(
            "CREATE TABLE scoring_log (experiment_id TEXT, round INTEGER, metric TEXT, value REAL, timestamp TEXT)"
        )
        cur.execute(
            "CREATE TABLE recommendation_log (experiment_id TEXT, round INTEGER, symbol TEXT, file_path TEXT, line_start INTEGER, line_end INTEGER, recommendation TEXT, context TEXT, timestamp TEXT)"
        )
        cur.execute(
            "INSERT INTO state_transition_log VALUES ('exp', 0, 'start', 'generate', 'first_round', 't')"
        )
        cur.execute(
            "INSERT INTO scoring_log VALUES ('exp', 0, 'maintainability_index', 80.0, 't')"
        )
        cur.execute(
            "INSERT INTO recommendation_log VALUES ('exp', 0, 'demo', 'demo.py', 1, 1, 'Add docstring', 'ctx', 't')"
        )
        conn.commit()
        conn.close()

    def tearDown(self) -> None:
        self.db_path.unlink(missing_ok=True)

    def test_load_and_visualize(self) -> None:
        logs = load_logs(self.db_path)
        self.assertIn("transition", logs)
        self.assertFalse(logs["transition"].empty)

        fig1 = build_state_transition_sankey(logs["transition"])
        fig2 = build_scoring_line_plot(logs["scoring"])
        fig3 = build_recommendation_bar_plot(logs["recommendation"])

        self.assertGreater(len(fig1.data), 0)
        self.assertGreater(len(fig2.data), 0)
        self.assertGreater(len(fig3.data), 0)


if __name__ == "__main__":
    unittest.main()
