from __future__ import annotations

from abc import ABC, abstractmethod

import json
from datetime import datetime, timezone
import subprocess

from ..factories.logging_provider import (
    LoggingMixin,
    LoggingProvider,
)
from ..utilities.metadata.logging.log_schemas import ToolInvocationLog


class ToolProviderBase(LoggingMixin, ABC):
    """Base class for running external tools."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def run(self, *args, experiment_id: str = "", round: int = 0, **kwargs):
        self._log.debug("Tool run start")
        params = json.dumps({"args": args, "kwargs": kwargs})
        result: subprocess.CompletedProcess | None = None
        success = False
        error_message = None
        try:
            result = self._run(*args, **kwargs)
            success = True
            return result
        except Exception as exc:
            error_message = str(exc)
            raise
        finally:
            stdout = (
                result.stdout
                if result is not None and hasattr(result, "stdout") and result.stdout
                else ""
            )
            stderr = (
                result.stderr
                if result is not None and hasattr(result, "stderr") and result.stderr
                else ""
            )
            return_code = (
                int(result.returncode)
                if result is not None and hasattr(result, "returncode")
                else 0
            )
            self.logger.log_tool_invocation(
                ToolInvocationLog(
                    experiment_id=str(experiment_id),
                    round=round,
                    tool_provider_name=self.__class__.__name__,
                    invocation_parameters=params,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=return_code,
                    success=success,
                    error_message=error_message,
                    timestamp=datetime.now(timezone.utc),
                )
            )
            self._log.debug("Tool run logged")

    @abstractmethod
    def _run(self, *args, **kwargs):
        """Run tool-specific logic."""
        raise NotImplementedError
