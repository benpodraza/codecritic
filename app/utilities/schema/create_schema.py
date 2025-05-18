from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, Type, Protocol, Any

from pydantic import BaseModel

from app.schemas import (
    AgentEngine,
    AgentPrompt,
    SystemPrompt,
    ContextProvider,
    ToolingProvider,
    FilePath,
    AgentConfig,
    PromptGenerator,
    ScoringProvider,
    StateManager,
    SystemConfig,
    ExperimentConfig,
    Series,
)
from app.utilities import db

class SchemaProtocol(Protocol):
    table_name: str
    __fields__: dict

    def __init__(self, **data: object) -> None:
        ...

    def model_dump(self) -> dict:
        ...


SchemaModel = Type[Any]

SCHEMAS: tuple[SchemaModel, ...] = (
    AgentEngine,
    AgentPrompt,
    SystemPrompt,
    ContextProvider,
    ToolingProvider,
    FilePath,
    AgentConfig,
    PromptGenerator,
    ScoringProvider,
    StateManager,
    SystemConfig,
    ExperimentConfig,
    Series,
)

TABLE_MAP = {model.table_name: model for model in SCHEMAS}


_TYPE_MAP = {
    int: "INTEGER",
    str: "TEXT",
    float: "REAL",
}


def _sqlite_type(py_type: Type) -> str:
    return _TYPE_MAP.get(py_type, "TEXT")


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for model in SCHEMAS:
        columns = []
        for name, field in model.__fields__.items():
            if name == "table_name":
                continue
            column = f"{name}"
            col_type = _sqlite_type(field.type_)
            if name == "id" and field.required is False:
                columns.append(f"{column} INTEGER PRIMARY KEY")
            else:
                columns.append(f"{column} {col_type}")
        col_sql = ",".join(columns)
        cur.execute(f"CREATE TABLE IF NOT EXISTS {model.table_name} ({col_sql})")
    conn.commit()


def load_seed_data(
    conn: sqlite3.Connection, seed_dir: Path | str = "experiments/config/seed"
) -> None:
    seed_path = Path(seed_dir)
    if not seed_path.exists():
        return
    cur = conn.cursor()
    for file in seed_path.glob("*.json"):
        model = TABLE_MAP.get(file.stem)
        if model is None:
            continue
        entries = json.loads(file.read_text())
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            obj = model(**entry)
            data = obj.model_dump()
            cols = ",".join(data.keys())
            placeholders = ",".join(["?"] * len(data))
            cur.execute(
                f"INSERT INTO {model.table_name} ({cols}) VALUES ({placeholders})",
                list(data.values()),
            )
    conn.commit()


def initialize_database() -> sqlite3.Connection:
    conn = db.get_connection()
    create_tables(conn)
    load_seed_data(conn)
    return conn


if __name__ == "__main__":  # pragma: no cover - manual invocation
    initialize_database()
