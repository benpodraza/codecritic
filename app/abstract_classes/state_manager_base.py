from __future__ import annotations

from abc import ABC, abstractmethod

from ..factories.logging_provider import LoggingMixin, LoggingProvider


class StateManagerBase(LoggingMixin, ABC):
    """Base class for managing state-level execution."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(self, *args, **kwargs) -> None:
        self._log.debug("StateManager run start")
        self._run_state_logic(*args, **kwargs)
        self._log.debug("StateManager run end")

    @abstractmethod
    def _run_state_logic(self, *args, **kwargs) -> None:
        """Execute state specific logic."""
        raise NotImplementedError
