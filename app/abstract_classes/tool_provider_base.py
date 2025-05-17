from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class ToolProviderBase(ABC):
    """Base class for running external tools."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self, *args, **kwargs):
        self.logger.debug("Tool run start")
        result = self._run(*args, **kwargs)
        self.logger.debug("Tool run end")
        return result

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Run tool-specific logic."""
        raise NotImplementedError
