import sqlite3
from pathlib import Path
from typing import Iterable, Any

DB_PATH = Path("experiments") / "codecritic.sqlite3"


def _serialize(obj: Any) -> dict:
    from dataclasses import asdict, is_dataclass
    from enum import Enum
    from pathlib import Path

    if not is_dataclass(obj) or isinstance(obj, type):
        raise TypeError(f"Expected dataclass instance, got {type(obj)}")

    result = asdict(obj)
    return {
        k: (str(v) if isinstance(v, (Path, Enum)) else v) for k, v in result.items()
    }


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db() -> sqlite3.Connection:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS state_log (
            experiment_id TEXT,
            system TEXT,
            round INTEGER,
            state TEXT,
            action TEXT,
            score REAL,
            details TEXT,
            timestamp TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS state_transition_log (
            experiment_id TEXT,
            round INTEGER,
            from_state TEXT,
            to_state TEXT,
            reason TEXT,
            timestamp TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS prompt_log (
            experiment_id TEXT,
            round INTEGER,
            system TEXT,
            agent_id TEXT,
            agent_role TEXT,
            agent_engine TEXT,
            symbol TEXT,
            prompt TEXT,
            response TEXT,
            attempt_number INTEGER,
            agent_action_outcome TEXT,
            start TEXT,
            stop TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS code_quality_log (
            experiment_id TEXT,
            round INTEGER,
            symbol TEXT,
            lines_of_code INTEGER,
            cyclomatic_complexity REAL,
            maintainability_index REAL,
            lint_errors INTEGER,
            timestamp TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS scoring_log (
            experiment_id TEXT,
            round INTEGER,
            metric TEXT,
            value REAL,
            timestamp TEXT
        )"""
    )
    conn.commit()
    return conn


def insert_logs(conn: sqlite3.Connection, table: str, logs: Iterable[Any]) -> None:
    logs = list(logs)
    if not logs:
        return
    row = _serialize(logs[0])
    cols = ",".join(row.keys())
    placeholders = ",".join(["?"] * len(row))
    values = [tuple(_serialize(log).values()) for log in logs]
    conn.executemany(
        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
