from __future__ import annotations

from abc import ABC, abstractmethod

import json
from datetime import datetime, timezone

from app.factories.logging_provider import LoggingMixin, LoggingProvider
from ..utilities.metadata.logging.log_schemas import SystemEventLog


class SystemManagerBase(LoggingMixin, ABC):
    """Base class for coordinating high level system logic."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(self, *args, experiment_id: str = "", round: int = 0, **kwargs) -> None:
        self._log.debug("SystemManager run start")
        params = json.dumps({"args": args, "kwargs": kwargs})
        success = False
        error_message = None
        try:
            self._run_system_logic(*args, **kwargs)
            success = True
        except Exception as exc:
            error_message = str(exc)
            raise
        finally:
            self.logger.log_system_event(
                SystemEventLog(
                    experiment_id=str(experiment_id),
                    round=round,
                    system_id=self.__class__.__name__,
                    event="run",
                    details=params,
                    success=success,
                    error_message=error_message,
                    timestamp=datetime.now(timezone.utc),
                )
            )
            self._log.debug("SystemManager run logged")

    @abstractmethod
    def _run_system_logic(self, *args, **kwargs) -> None:
        """Execute system-specific logic and state transitions."""
        raise NotImplementedError
