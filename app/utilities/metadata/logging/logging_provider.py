from __future__ import annotations

from datetime import datetime
import json
import logging
import sqlite3
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Iterable
from app.db.connection import get_connection
from app.enums.logging_enums import LOG_TYPE
from app.db.schemas import (
    SnapshotMetricsSchema,
    StateTransitionLogSchema,
    AgentConversationLogSchema,
    ErrorLogSchema,
    ProviderLogSchema,
    FileLogSchema
)

LOG_CONFIG_MAP = {
    LOG_TYPE.STATE_TRANSITION: {
        "schema": StateTransitionLogSchema,
        "table": "state_transition_log",
    },
    LOG_TYPE.AGENT_CONVERSATION: {
        "schema": AgentConversationLogSchema,
        "table": "agent_conversation_log",
    },
    LOG_TYPE.PROVIDER: {
        "schema": ProviderLogSchema,
        "table": "provider_log",
    },
    LOG_TYPE.ERROR: {
        "schema": ErrorLogSchema,
        "table": "error_log",
    },
    LOG_TYPE.SNAPSHOT_METRICS: {
        "schema": SnapshotMetricsSchema,  
        "table": "snapshot_metrics",   
    },
    LOG_TYPE.FILE: {  
        "schema": FileLogSchema,
        "table": "file_log",
    },
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
            if connection is not None:
                self._conn = connection
            return

        from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

        self.fm = get_file_manager()
        self.db_path = self.fm._resolve(FILETYPE.DATABASE, db_path)
        self._conn = connection or get_connection()

        self.output_path = None
        if output_path:
            self.fm.makedirs(FILETYPE.LOG)
            # Just store filename – write will resolve again to current file manager
            self.output_path = Path(output_path).name

        self._initialized = True

    @property
    def conn(self):
        if getattr(self, "_conn", None) is None:
            from app.db import init_db
            self._conn = init_db(reset=False).raw_connection()
        try:
            self._conn.cursor()
        except Exception:
            from app.db import init_db
            self._conn = init_db(reset=False).raw_connection()
        return self._conn

    def _serialize(self, obj: Any) -> dict:
        def _safe(v: Any) -> Any:
            if isinstance(v, (Enum, Path)):
                return str(v)
            elif isinstance(v, datetime):
                return v.isoformat()
            elif isinstance(v, list):
                # ✅ Serialize list directly
                return json.dumps([_safe(i) for i in v])
            elif isinstance(v, dict):
                # ✅ Serialize dict directly
                return json.dumps({k: _safe(val) for k, val in v.items()})
            return v

        if not is_dataclass(obj) or isinstance(obj, type):
            raise TypeError(f"Expected dataclass instance, got {type(obj)}")

        raw = asdict(obj)
        return {k: _safe(v) for k, v in raw.items()}



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
            for item in items:
                self.fm.save_append(FILETYPE.LOG, self.output_path, json.dumps(item) + "\n")

    def write(self, log_type: LOG_TYPE, entries: list[Any] | Any) -> int | None:
        if not isinstance(entries, list):
            entries = [entries]

        config = LOG_CONFIG_MAP.get(log_type)
        if config is None:
            raise ValueError(f"Unsupported log type: {log_type}")

        schema_cls = config["schema"]
        table_name = config["table"]

        for entry in entries:
            if not is_dataclass(entry):
                raise TypeError(f"Expected a dataclass instance, got {type(entry)}")
            if entry.__class__.__name__ != schema_cls.__name__:
                logging.getLogger("LoggingProvider").warning(
                    f"⚠️ Log schema mismatch: expected {schema_cls.__name__}, got {entry.__class__.__name__}"
                )

        serialized = [self._serialize(e) for e in entries]
        
        cur = self.conn.cursor()

        if len(serialized) == 1:
            keys = list(serialized[0].keys())
            cols = ",".join(keys)
            placeholders = ",".join(["?"] * len(keys))
            values = tuple(serialized[0][k] for k in keys)

            cur.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", values)
            self.conn.commit()

            return cur.lastrowid  # ✅ Return the inserted row ID

        # If multiple, just bulk insert without return
        self._insert_many(table_name, serialized)
        return None

    def log_provider(self, log: ProviderLogSchema) -> None:
        self.write(LOG_TYPE.PROVIDER, log)

    def log_state_transition(self, log: StateTransitionLogSchema) -> None:
        self.write(LOG_TYPE.STATE_TRANSITION, log)

    def log_agent_conversation(self, log: AgentConversationLogSchema) -> None:
        self.write(LOG_TYPE.AGENT_CONVERSATION, log)

    def log_error(self, log: ErrorLogSchema) -> None:
        self.write(LOG_TYPE.ERROR, log)

    def log_snapshot_metrics(self, log: SnapshotMetricsSchema) -> None:
        self.write(LOG_TYPE.SNAPSHOT_METRICS, log)
    
    def log_file(self, log: FileLogSchema) -> None:
        self.write(LOG_TYPE.FILE, log)

    def close(self) -> None:
        self.conn.close()


class LoggingMixin:
    """Mixin to provide access to a shared LoggingProvider instance."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        self.logger = logger or LoggingProvider()
        self._log = logging.getLogger(self.__class__.__name__)

    def log_provider(self, log: ProviderLogSchema) -> None:
        self.logger.log_provider(log)

    def log_state_transition(self, log: StateTransitionLogSchema) -> None:
        self.logger.log_state_transition(log)

    def log_agent_conversation(self, log: AgentConversationLogSchema) -> None:
        self.logger.log_agent_conversation(log)

    def log_error(self, log: ErrorLogSchema) -> None:
        self.logger.log_error(log)

    def log_snapshot_metrics(self, log: SnapshotMetricsSchema) -> None:
        self.logger.log_snapshot_metrics(log)
    
    def log_file(self, log: FileLogSchema) -> None:
        self.logger.log_file(log)
