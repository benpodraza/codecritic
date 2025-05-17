from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class AgentBase(ABC):
    """Base class for executing agent logic."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, *args, **kwargs) -> None:
        self.logger.debug("Agent run start")
        self._run_agent_logic(*args, **kwargs)
        self.logger.debug("Agent run end")

    @abstractmethod
    def _run_agent_logic(self, *args, **kwargs) -> None:
        """Execute agent specific logic."""
        raise NotImplementedError
