from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from app.db.schemas import ToolConfig
from app.factories.logging_provider import LoggingMixin, LoggingProvider, LogType
from app.utilities.metadata.logging.log_schemas import ToolInvocationLog, ErrorLog

class ToolProviderBase(LoggingMixin, ABC):
    """Base class for running external tools."""

    def __init__(self, tool_config: ToolConfig, logger: LoggingProvider | None = None):
        super().__init__(logger)
        self.tool_config = tool_config

    def run(self, *args, experiment_id: str, round: int, **kwargs):
        self._log.debug("Tool run start")
        params = json.dumps({"args": args, "kwargs": kwargs})
        result: subprocess.CompletedProcess | None = None
        success = False
        error_message = None

        try:
            result = self._run(*args, **kwargs)
            success = result.returncode == 0
            return result
        except Exception as exc:
            error_message = str(exc)
            error_log = ErrorLog(
                experiment_id=experiment_id,
                round=round,
                error_type=type(exc).__name__,
                message=error_message,
                file_path=str(Path(__file__).resolve()),
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LogType.ERROR, error_log)
            self._log.error("Critical tool run error logged: %s", error_message)
            raise
        finally:
            stdout = result.stdout if result and result.stdout else ""
            stderr = result.stderr if result and result.stderr else ""
            return_code = result.returncode if result else -1

            invocation_log =  ToolInvocationLog(
                experiment_id=str(experiment_id),
                round=round,
                tool_provider_name=self.__class__.__name__,
                tool_provider_guid=self.tool_config.guid,
                invocation_parameters=params,
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                success=success,
                error_message=error_message,
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LogType.TOOL_INVOCATION, invocation_log)
            self._log.debug("Tool run logged")

    @abstractmethod
    def _run(self, *args, **kwargs):
        raise NotImplementedError
