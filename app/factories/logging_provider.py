from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, Union
from dataclasses import asdict, is_dataclass

from app.enums.logging_enums import LogType
from app.utilities.db import get_connection
from app.utilities.metadata.logging.log_schemas import (
    StateLog,
    StateTransitionLog,
    PromptLog,
    CodeQualityLog,
    ErrorLog,
    ScoringLog,
    ConversationLog,
    ExperimentLog,
)

# Optional: map LogType to dataclass
LOG_MODEL_MAP = {
    LogType.STATE: StateLog,
    LogType.STATE_TRANSITION: StateTransitionLog,
    LogType.PROMPT: PromptLog,
    LogType.CODE_QUALITY: CodeQualityLog,
    LogType.ERROR: ErrorLog,
    LogType.SCORING: ScoringLog,
    LogType.CONVERSATION: ConversationLog,
    LogType.EXPERIMENT: ExperimentLog,
}


class LoggingProvider:
    def __init__(self, db_path: str | Path = "experiments/codecritic.sqlite3") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        self.conn: sqlite3.Connection = get_connection()

    def _serialize(self, obj: Any) -> dict:
        if not is_dataclass(obj) or isinstance(obj, type):
            raise TypeError(f"Expected dataclass instance, got {type(obj)}")
        return asdict(obj)

    def _insert_many(self, table: str, items: Iterable[dict]) -> None:
        cur = self.conn.cursor()
        if not items:
            return
        keys = items[0].keys()
        cols = ",".join(keys)
        placeholders = ",".join(["?"] * len(keys))
        values = [tuple(i[k] for k in keys) for i in items]
        cur.executemany(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
        self.conn.commit()

    def write(self, log_type: LogType, entries: Union[list[Any], Any]) -> None:
        if not isinstance(entries, list):
            entries = [entries]
        model_cls = LOG_MODEL_MAP.get(log_type)
        if model_cls is None:
            raise ValueError(f"Unsupported log type: {log_type}")
        for entry in entries:
            if not isinstance(entry, model_cls):
                raise TypeError(f"Expected {model_cls.__name__}, got {type(entry)}")
        serialized = [self._serialize(e) for e in entries]
        self._insert_many(log_type.value + "_log", serialized)

    def close(self):
        self.conn.close()


# Example usage:
# logger = LoggingProvider()
# logger.write(LogType.STATE, StateLog(...))
# logger.write(LogType.ERROR, [ErrorLog(...), ErrorLog(...)])
