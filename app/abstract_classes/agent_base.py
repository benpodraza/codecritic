from __future__ import annotations

from abc import ABC, abstractmethod

from ..utilities.metadata.logging import LoggingMixin, LoggingProvider


class AgentBase(LoggingMixin, ABC):
    """Base class for executing agent logic."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(self, *args, **kwargs) -> None:
        self._log.debug("Agent run start")
        self._run_agent_logic(*args, **kwargs)
        self._log.debug("Agent run end")

    @abstractmethod
    def _run_agent_logic(self, *args, **kwargs) -> None:
        """Execute agent specific logic."""
        raise NotImplementedError
