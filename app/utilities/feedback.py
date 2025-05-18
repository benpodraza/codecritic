from __future__ import annotations

from typing import ClassVar, Dict, List

from .metadata.logging.log_schemas import FeedbackLog


class FeedbackRepository:
    """In-memory store for feedback logs."""

    _data: ClassVar[Dict[str, List[FeedbackLog]]] = {}

    @classmethod
    def add_feedback(cls, log: FeedbackLog) -> None:
        cls._data.setdefault(log.experiment_id, []).append(log)

    @classmethod
    def get_feedback(cls, experiment_id: str) -> List[FeedbackLog]:
        return list(cls._data.get(experiment_id, []))

    @classmethod
    def clear(cls) -> None:
        cls._data.clear()
