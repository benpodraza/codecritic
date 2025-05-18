from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Type, Any, Union, get_origin, get_args
from enum import Enum

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

SCHEMAS = {
    "agent_engine": AgentEngine,
    "agent_prompt": AgentPrompt,
    "system_prompt": SystemPrompt,
    "context_provider": ContextProvider,
    "tooling_provider": ToolingProvider,
    "file_path": FilePath,
    "agent_config": AgentConfig,
    "prompt_generator": PromptGenerator,
    "scoring_provider": ScoringProvider,
    "state_manager": StateManager,
    "system_config": SystemConfig,
    "experiment_config": ExperimentConfig,
    "series": Series,
}

_TYPE_MAP = {
    int: "INTEGER",
    str: "TEXT",
    float: "REAL",
    Path: "TEXT",
}


def _sqlite_type(py_type: Type) -> str:
    origin = get_origin(py_type)
    if origin is Union:
        py_type = get_args(py_type)[0]
    return _TYPE_MAP.get(py_type, "TEXT")


def _is_optional(annotation: Any) -> bool:
    return get_origin(annotation) is Union and type(None) in get_args(annotation)


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table_name, model_cls in SCHEMAS.items():
        fields = model_cls.__annotations__
        columns = []
        for name, annotation in fields.items():
            col_type = _sqlite_type(annotation)
            if name == "id" and _is_optional(annotation):
                columns.append(f"{name} INTEGER PRIMARY KEY")
            else:
                columns.append(f"{name} {col_type}")
        col_sql = ", ".join(columns)
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({col_sql})")
    conn.commit()


def load_seed_data(
    conn: sqlite3.Connection, seed_dir: Path | str = "experiments/config/seed"
) -> None:
    seed_path = Path(seed_dir)
    if not seed_path.exists():
        return
    cur = conn.cursor()
    for file in seed_path.glob("*.json"):
        print(f"Reading seed file: {file.name}")
        table_name = file.stem
        model = SCHEMAS.get(table_name)
        if model is None:
            continue
        entries = json.loads(file.read_text())
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            obj = model(**entry)
            data = obj.model_dump()
            # Convert enums and paths to strings
            data = {
                k: str(v) if isinstance(v, (Path, Enum)) else v for k, v in data.items()
            }
            cols = ",".join(data.keys())
            placeholders = ",".join(["?"] * len(data))
            cur.execute(
                f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})",
                list(data.values()),
            )
    conn.commit()


def initialize_database(reset: bool = False) -> sqlite3.Connection:
    db_path = Path("experiments/codecritic.sqlite3")

    if reset and db_path.exists():
        try:
            import sqlite3

            sqlite3.connect(str(db_path)).close()
        except Exception:
            pass
        import gc

        gc.collect()
        db_path.unlink()

    conn = db.get_connection()
    create_tables(conn)
    load_seed_data(conn)
    return conn


if __name__ == "__main__":
    initialize_database()
