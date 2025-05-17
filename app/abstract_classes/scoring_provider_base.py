from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class ScoringProviderBase(ABC):
    """Base class for computing evaluation metrics."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def score(self, *args, **kwargs):
        self.logger.debug("Scoring start")
        result = self._score(*args, **kwargs)
        self.logger.debug("Scoring end")
        return result

    @abstractmethod
    def _score(self, *args, **kwargs):
        """Compute evaluation metrics."""
        raise NotImplementedError
