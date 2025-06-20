from pathlib import Path
import sqlite3
import gc

from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

DB_FILENAME = "codecritic.sqlite3"
fm = get_file_manager()
DB_PATH = fm.resolve(FILETYPE.DATABASE, DB_FILENAME)
_CONN: sqlite3.Connection | None = None

def get_connection() -> sqlite3.Connection:
    global _CONN
    try:
        if _CONN is None:
            raise RuntimeError
        _CONN.execute("SELECT 1")
    except (sqlite3.ProgrammingError, RuntimeError):
        _CONN = sqlite3.connect(DB_PATH, check_same_thread=False)
    return _CONN

def close_connection() -> None:
    global _CONN
    if _CONN:
        _CONN.close()
        _CONN = None
