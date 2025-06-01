#  base_provider.py
from abc import abstractmethod
from datetime import datetime, timezone
from pathlib import Path
import json

from app.utilities.metadata.logging.logging_provider import LoggingMixin, LogType
from app.db.schemas import ProviderLogSchema, ErrorLogSchema


class BaseProvider(LoggingMixin):
    """Base class for all providers using a unified provider log."""

    def __init__(self, config=None, engine=None) -> None:
        super().__init__()  # initializes LoggingProvider and _log
        assert engine is not None, "🚨 engine must be injected into BaseProvider"
        self.config = config
        self._engine = engine

    def run(self, input: dict | None = None, session_id: str = "") -> str:
        input = input or {}
        self._log.debug("Run started")
        self._session_id = session_id
        self._system = input.get("system", "unknown")
        output = None

        try:
            output = self._run_provider(input)
            return output
        except Exception as exc:
            # Log the error
            self.logger.write(
                LogType.ERROR,
                ErrorLogSchema(
                    session_id=session_id,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    file_path=str(Path(__file__).relative_to(Path.cwd())),
                ),
            )
            raise
        finally:
            # Log the provider call (successful or not)
            log = ProviderLogSchema(
                session_id=session_id,
                provider_id=self.config.id if self.config else -1,
                provider_type=next(
                    base.__name__
                    for base in self.__class__.__mro__
                    if base.__name__.endswith("ProviderBase") and base is not object
                ),
                input=json.dumps(input),
                output=json.dumps(output.model_dump())
                if hasattr(output, "model_dump")
                else json.dumps(output),
                file_path=getattr(self.config, "artifact_path", None),
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LogType.PROVIDER, log)
            self._log.debug("Run logged")

    @abstractmethod
    def _run_provider(self, input: dict) -> str:
        raise NotImplementedError
