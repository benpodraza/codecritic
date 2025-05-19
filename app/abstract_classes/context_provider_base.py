from __future__ import annotations

from abc import ABC, abstractmethod

import json
from datetime import datetime, timezone

from ..factories.logging_provider import (
    LoggingMixin,
    LoggingProvider,
)
from ..utilities.metadata.logging.log_schemas import ContextRetrievalLog


class ContextProviderBase(LoggingMixin, ABC):
    """Base class for providing context from symbol graphs."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def get_context(self, *args, experiment_id: str = "", round: int = 0, **kwargs):
        self._log.debug("Context retrieval start")
        params = json.dumps({"args": args, "kwargs": kwargs})
        context = None
        success = False
        error_message = None
        try:
            context = self._get_context(*args, **kwargs)
            success = True
            return context
        except Exception as exc:
            error_message = str(exc)
            raise
        finally:
            self.logger.log_context_retrieval(
                ContextRetrievalLog(
                    experiment_id=str(experiment_id),
                    round=round,
                    context_provider_name=self.__class__.__name__,
                    context_parameters=params,
                    retrieved_context=(
                        json.dumps(context, default=str) if success else ""
                    ),
                    success=success,
                    error_message=error_message,
                    timestamp=datetime.now(timezone.utc),
                )
            )
            self._log.debug("Context retrieval logged")

    @abstractmethod
    def _get_context(self, *args, **kwargs):
        """Return context information."""
        raise NotImplementedError
