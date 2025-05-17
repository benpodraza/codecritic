from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class SystemManagerBase(ABC):
    """Base class for coordinating high level system logic."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, *args, **kwargs) -> None:
        self.logger.debug("SystemManager run start")
        self._run_system_logic(*args, **kwargs)
        self.logger.debug("SystemManager run end")

    @abstractmethod
    def _run_system_logic(self, *args, **kwargs) -> None:
        """Execute system-specific logic and state transitions."""
        raise NotImplementedError
