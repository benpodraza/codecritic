from __future__ import annotations

from abc import ABC, abstractmethod

import json
from datetime import datetime, timezone

from ..factories.logging_provider import (
    LoggingMixin,
    LoggingProvider,
)
from ..utilities.metadata.logging.log_schemas import AgentActionLog


class AgentBase(LoggingMixin, ABC):
    """Base class for executing agent logic."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(
        self,
        *args,
        experiment_id: str = "",
        round: int = 0,
        action: str = "run",
        **kwargs,
    ) -> None:
        self._log.debug("Agent run start")
        params = json.dumps({"args": args, "kwargs": kwargs})
        response = ""
        success = False
        error_message = None
        try:
            self._run_agent_logic(*args, **kwargs)
            success = True
        except Exception as exc:
            error_message = str(exc)
            raise
        finally:
            self.logger.log_agent_action(
                AgentActionLog(
                    experiment_id=str(experiment_id),
                    round=round,
                    agent_id=self.__class__.__name__,
                    agent_role=getattr(self, "role", ""),
                    action=action,
                    parameters=params,
                    response=response,
                    success=success,
                    error_message=error_message,
                    timestamp=datetime.now(timezone.utc),
                )
            )
            self._log.debug("Agent run logged")

    @abstractmethod
    def _run_agent_logic(self, *args, **kwargs) -> None:
        """Execute agent specific logic."""
        raise NotImplementedError
