from __future__ import annotations

from abc import ABC, abstractmethod

from ..factories.logging_provider import LoggingMixin, LoggingProvider


class ContextProviderBase(LoggingMixin, ABC):
    """Base class for providing context from symbol graphs."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def get_context(self, *args, **kwargs):
        self._log.debug("Context retrieval start")
        context = self._get_context(*args, **kwargs)
        self._log.debug("Context retrieval end")
        return context

    @abstractmethod
    def _get_context(self, *args, **kwargs):
        """Return context information."""
        raise NotImplementedError
