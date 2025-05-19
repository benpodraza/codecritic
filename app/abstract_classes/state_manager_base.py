from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable

from ..factories.logging_provider import LoggingMixin, LoggingProvider


class StateManagerBase(LoggingMixin, ABC):
    """Base class for managing state-level execution and transitions."""

    def __init__(
        self,
        scoring_function: Callable[[Any], float] | None = None,
        context_manager: Any | None = None,
        logger: LoggingProvider | None = None,
    ) -> None:
        super().__init__(logger)
        self.scoring_function = scoring_function
        self.context_manager = context_manager

    def run(self, *args, **kwargs) -> None:
        self._log.debug("StateManager run start")
        self._run_state_logic(*args, **kwargs)
        self._log.debug("StateManager run end")

    @abstractmethod
    def _run_state_logic(self, *args, **kwargs) -> None:
        """Execute state specific logic."""
        raise NotImplementedError

    @abstractmethod
    def transition_state(
        self,
        experiment_id: str,
        round: int,
        from_state: Enum,
        to_state: Enum,
        reason: str,
    ) -> None:
        """Abstract method explicitly defining logic for transitioning states."""
        raise NotImplementedError
