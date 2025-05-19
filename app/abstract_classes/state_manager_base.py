from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

from app.utilities.metadata.logging.log_schemas import (
    ErrorLog,
    StateTransitionLog,
    StateLog,
)
from app.factories.logging_provider import LoggingMixin, LoggingProvider, LogType
from app.enums.system_enums import StateTransitionReason, SystemState


class StateManagerBase(LoggingMixin, ABC):
    """Base class for managing state lifecycle and transitions."""

    def __init__(
        self,
        scoring_function,
        context_manager,
        agent,
        logger: LoggingProvider | None = None,
    ) -> None:
        super().__init__(logger)
        self.scoring_function = scoring_function
        self.context_manager = context_manager
        self.agent = agent
        self.current_state = SystemState.START

    def run_state(
        self,
        experiment_id: str,
        system: str,
        state: SystemState,
        round: int,
        *args,
        **kwargs,
    ) -> None:
        self._log.debug("State logic execution start")
        error_message = None
        details = None

        try:
            self._run_state_logic(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            error_log = ErrorLog(
                experiment_id=experiment_id,
                round=round,
                error_type=type(e).__name__,
                message=error_message,
                file_path=str(Path(__file__).relative_to(Path.cwd())),
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LogType.ERROR, error_log)
            self._log.error("State logic execution error logged: %s", error_message)
            raise
        finally:
            lifecycle_log = StateLog(
                experiment_id=experiment_id,
                system=system,
                round=round,
                state=state,
                action="run_state_logic",
                score=None,
                details=details or error_message,
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LogType.STATE, lifecycle_log)
            self._log.debug("State lifecycle logged")

    @abstractmethod
    def _run_state_logic(self, *args, **kwargs) -> None:
        """Implement specific logic for the state."""
        raise NotImplementedError
