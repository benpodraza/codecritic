from __future__ import annotations

from abc import ABC, abstractmethod

from ..utilities.metadata.logging import LoggingMixin, LoggingProvider


class SystemManagerBase(LoggingMixin, ABC):
    """Base class for coordinating high level system logic."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(self, *args, **kwargs) -> None:
        self._log.debug("SystemManager run start")
        self._run_system_logic(*args, **kwargs)
        self._log.debug("SystemManager run end")

    @abstractmethod
    def _run_system_logic(self, *args, **kwargs) -> None:
        """Execute system-specific logic and state transitions."""
        raise NotImplementedError
