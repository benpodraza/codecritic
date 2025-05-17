# app/utils/logging/log_writers.py

from pathlib import Path
from pydantic import BaseModel
from app.schemas.logging_schemas import (
    StateTransitionLog,
    StateLog,
    PromptLog,
    ConversationLog,
    ErrorLog,
    ExperimentLog,
    EvaluationLog
)

class BaseLogger:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, entry: BaseModel):
        with self.file_path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")


class StateTransitionLogger(BaseLogger):
    def log(self, **kwargs):
        entry = StateTransitionLog(**kwargs)
        self._write(entry)


class StateLogger(BaseLogger):
    def log(self, **kwargs):
        entry = StateLog(**kwargs)
        self._write(entry)


class PromptLogger(BaseLogger):
    def log(self, **kwargs):
        entry = PromptLog(**kwargs)
        self._write(entry)


class ConversationLogger(BaseLogger):
    def log(self, **kwargs):
        entry = ConversationLog(**kwargs)
        self._write(entry)


class ErrorLogger(BaseLogger):
    def log(self, **kwargs):
        entry = ErrorLog(**kwargs)
        self._write(entry)


class ExperimentLogger(BaseLogger):
    def log(self, **kwargs):
        entry = ExperimentLog(**kwargs)
        self._write(entry)


class EvaluationLogger(BaseLogger):
    def log(self, **kwargs):
        entry = EvaluationLog(**kwargs)
        self._write(entry)
