from __future__ import annotations

from abc import ABC, abstractmethod

from ..utilities.metadata.logging import LoggingMixin, LoggingProvider


class ScoringProviderBase(LoggingMixin, ABC):
    """Base class for computing evaluation metrics."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def score(self, *args, **kwargs):
        self._log.debug("Scoring start")
        result = self._score(*args, **kwargs)
        self._log.debug("Scoring end")
        return result

    @abstractmethod
    def _score(self, *args, **kwargs):
        """Compute evaluation metrics."""
        raise NotImplementedError
