from __future__ import annotations

from datetime import datetime
import json
import logging
import sqlite3
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Iterable

from app.enums.logging_enums import LogType
from ..utilities.metadata.logging.log_schemas import (
    StateLog,
    StateTransitionLog,
    PromptLog,
    CodeQualityLog,
    ErrorLog,
    ScoringLog,
    ConversationLog,
    ExperimentLog,
    RecommendationLog,
)


LOG_MODEL_MAP = {
    LogType.STATE: StateLog,
    LogType.STATE_TRANSITION: StateTransitionLog,
    LogType.PROMPT: PromptLog,
    LogType.CODE_QUALITY: CodeQualityLog,
    LogType.ERROR: ErrorLog,
    LogType.SCORING: ScoringLog,
    LogType.CONVERSATION: ConversationLog,
    LogType.EXPERIMENT: ExperimentLog,
    LogType.RECOMMENDATION: RecommendationLog,
}


class LoggingProvider:
    """Centralized provider for structured logging."""

    _instance: ClassVar["LoggingProvider" | None] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        db_path: str | Path = "experiments/codecritic.sqlite3",
        output_path: str | Path | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> None:
        if getattr(self, "_initialized", False):
            return

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        from app.utilities.db import get_connection, init_db

        if connection:
            self.conn = connection
            init_db(self.conn)
        else:
            self.conn = get_connection()
            init_db()

        self.output_path = Path(output_path) if output_path else None
        if self.output_path:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialized = True

    def _serialize(self, obj: Any) -> dict:
        def _safe(v: Any) -> Any:
            if isinstance(v, (Enum, Path)):
                return str(v)
            elif isinstance(v, datetime):
                return v.isoformat()
            elif isinstance(v, list):
                return [_safe(i) for i in v]
            elif isinstance(v, dict):
                return {k: _safe(val) for k, val in v.items()}
            return v

        if not is_dataclass(obj) or isinstance(obj, type):
            raise TypeError(f"Expected dataclass instance, got {type(obj)}")
        return _safe(asdict(obj))

    def _insert_many(self, table: str, items: Iterable[dict]) -> None:
        items = list(items)
        if not items:
            return
        keys = list(items[0].keys())
        cols = ",".join(keys)
        placeholders = ",".join(["?"] * len(keys))
        values = [tuple(i[k] for k in keys) for i in items]
        cur = self.conn.cursor()
        cur.executemany(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
        self.conn.commit()
        if self.output_path:
            with self.output_path.open("a", encoding="utf-8") as fh:
                for item in items:
                    fh.write(json.dumps(item) + "\n")

    def write(self, log_type: LogType, entries: list[Any] | Any) -> None:
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

    # Convenience wrappers
    def log_state(self, log: StateLog) -> None:
        self.write(LogType.STATE, log)

    def log_transition(self, log: StateTransitionLog) -> None:
        self.write(LogType.STATE_TRANSITION, log)

    def log_prompt(self, log: PromptLog) -> None:
        self.write(LogType.PROMPT, log)

    def log_code_quality(self, log: CodeQualityLog) -> None:
        self.write(LogType.CODE_QUALITY, log)

    def log_error(self, log: ErrorLog) -> None:
        self.write(LogType.ERROR, log)

    def log_scoring(self, log: ScoringLog) -> None:
        self.write(LogType.SCORING, log)

    def log_conversation(self, log: ConversationLog) -> None:
        self.write(LogType.CONVERSATION, log)

    def log_experiment(self, log: ExperimentLog) -> None:
        self.write(LogType.EXPERIMENT, log)

    def log_recommendation(self, log: RecommendationLog) -> None:
        self.write(LogType.RECOMMENDATION, log)

    def close(self) -> None:
        self.conn.close()


class LoggingMixin:
    """Mixin to provide access to a shared LoggingProvider instance."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        self.logger = logger or LoggingProvider()
        self._log = logging.getLogger(self.__class__.__name__)

    def log_state(self, log: StateLog) -> None:
        self.logger.log_state(log)

    def log_transition(self, log: StateTransitionLog) -> None:
        self.logger.log_transition(log)

    def log_prompt(self, log: PromptLog) -> None:
        self.logger.log_prompt(log)

    def log_code_quality(self, log: CodeQualityLog) -> None:
        self.logger.log_code_quality(log)

    def log_error(self, log: ErrorLog) -> None:
        self.logger.log_error(log)

    def log_scoring(self, log: ScoringLog) -> None:
        self.logger.log_scoring(log)

    def log_conversation(self, log: ConversationLog) -> None:
        self.logger.log_conversation(log)

    def log_experiment(self, log: ExperimentLog) -> None:
        self.logger.log_experiment(log)

    def log_recommendation(self, log: RecommendationLog) -> None:
        self.logger.log_recommendation(log)
