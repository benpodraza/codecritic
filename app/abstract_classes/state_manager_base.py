from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class StateManagerBase(ABC):
    """Base class for managing state-level execution."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, *args, **kwargs) -> None:
        self.logger.debug("StateManager run start")
        self._run_state_logic(*args, **kwargs)
        self.logger.debug("StateManager run end")

    @abstractmethod
    def _run_state_logic(self, *args, **kwargs) -> None:
        """Execute state specific logic."""
        raise NotImplementedError
