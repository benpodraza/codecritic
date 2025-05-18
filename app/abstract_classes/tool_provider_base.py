from __future__ import annotations

from abc import ABC, abstractmethod

from ..factories.logging_provider import LoggingMixin, LoggingProvider


class ToolProviderBase(LoggingMixin, ABC):
    """Base class for running external tools."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(self, *args, **kwargs):
        self._log.debug("Tool run start")
        result = self._run(*args, **kwargs)
        self._log.debug("Tool run end")
        return result

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Run tool-specific logic."""
        raise NotImplementedError
