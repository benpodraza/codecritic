from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class ContextProviderBase(ABC):
    """Base class for providing context from symbol graphs."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_context(self, *args, **kwargs):
        self.logger.debug("Context retrieval start")
        context = self._get_context(*args, **kwargs)
        self.logger.debug("Context retrieval end")
        return context

    @abstractmethod
    def _get_context(self, *args, **kwargs):
        """Return context information."""
        raise NotImplementedError
