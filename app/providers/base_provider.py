from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timezone
from pathlib import Path
import json

from app.utilities.metadata.logging.logging_provider import LoggingMixin, LogType
from app.db.schemas import ProviderLogSchema, ErrorLogSchema

class BaseProvider(LoggingMixin):
    """Base class for all providers using unified provider log."""

    def __init__(self, config=None, engine=None) -> None:
        super().__init__()
        self.config = config
        self._engine = engine

    def run(self, input: dict, session_id: str) -> str:
        self._log.debug("Run started")
        self._session_id = session_id
        self._system = input.get("system", "unknown")
        output = None

        try:
            output = self._run_provider(input)
            return output
        except Exception as exc:
            self.logger.write(LogType.ERROR, ErrorLogSchema(
                session_id=session_id,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=str(Path(__file__).relative_to(Path.cwd())),
            ))
            raise
        finally:
            log = ProviderLogSchema(
                session_id=session_id,
                provider_id=self.config.id if self.config else -1,
                provider_type = next(
                    base.__name__
                    for base in self.__class__.__mro__
                    if base.__name__.endswith("ProviderBase") and base is not object
                ),
                input=json.dumps(input),
                output=json.dumps(output.model_dump()) if hasattr(output, "model_dump") else json.dumps(output),
                file_path = getattr(self.config, "artifact_path", None),
                timestamp=datetime.now(timezone.utc)
            )
            self.logger.write(LogType.PROVIDER, log)
            self._log.debug("Run logged")

    def resolve_dependencies(self, **kwargs) -> None:
        """Automatically wire known dependencies and enable reverse injection."""
        for name, dep in kwargs.items():
            if dep is None:
                continue

            # Set reference
            setattr(self, name, dep)

            # Reverse registration for context or score providers
            if name in {"context_provider", "score_provider"}:
                method = f"set_{self.__class__.__name__.lower()}"
                if hasattr(dep, method):
                    getattr(dep, method)(self)

            # Handle list of tool providers
            elif name == "tool_providers" and isinstance(dep, list):
                for tool in dep:
                    if hasattr(tool, "set_context_provider") and hasattr(self, "context_provider"):
                        tool.set_context_provider(self.context_provider)
                    if hasattr(tool, "set_score_provider") and hasattr(self, "score_provider"):
                        tool.set_score_provider(self.score_provider)

    @abstractmethod
    def _run_provider(self, input: dict) -> str:
        raise NotImplementedError
