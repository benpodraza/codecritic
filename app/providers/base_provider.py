from abc import abstractmethod
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Optional

from app.utilities.metadata.logging.logging_provider import LoggingMixin, LOG_TYPE
from app.db.schemas import ProviderLogSchema, ErrorLogSchema
from app.enums.logging_enums import PROVIDER_TYPE
from app.enums.logging_enums import ERROR_TYPE


class BaseProvider(LoggingMixin):
    def __init__(self, config=None, engine=None) -> None:
        super().__init__()
        assert engine is not None, "🚨 engine must be injected into BaseProvider"
        self.config = config
        self._engine = engine

    def run(self, input: dict | None = None, session_id: str = "") -> str:
        input = input or {}
        self._session_id = session_id
        self._system = input.get("system", "unknown")

        start_time = time.perf_counter()
        output = None
        output_schema = None

        try:
            output = self._run_provider(input)
            if hasattr(output, "json"):
                output_schema = output.__class__.__name__
        except Exception as exc:
            self.logger.write(
                LOG_TYPE.ERROR,
                ErrorLogSchema(
                    session_id=session_id,
                    error_type=self._map_error_type(exc),
                    message=str(exc),
                    file_path=str(Path(__file__).relative_to(Path.cwd())),
                    provider_id=self.config.id if self.config else None,
                    provider_type=self._infer_provider_type(),
                    timestamp=datetime.now(timezone.utc),
                ),
            )
            raise
        finally:
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Serialize the input and output properly
            log = ProviderLogSchema(
                session_id=session_id,
                provider_id=self.config.id if self.config else -1,
                provider_type=self._infer_provider_type(),
                input=json.dumps({k: v.dict() if hasattr(v, "dict") else v for k, v in input.items()}),
                output=json.dumps(output.dict() if hasattr(output, "dict") else output),
                output_schema=output_schema,
                latency_ms=latency_ms,
                config_hash=self._compute_config_hash(),
                file_path=getattr(self.config, "artifact_path", None),
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LOG_TYPE.PROVIDER, log)
            self._log.debug("✅ Provider run logged")

        return output

    def _map_error_type(self, exc: Exception) -> ERROR_TYPE:
        return ERROR_TYPE.RUNTIME

    def _infer_provider_type(self) -> PROVIDER_TYPE:
        cls = self.__class__.__name__.lower()
        if "tool" in cls:
            return PROVIDER_TYPE.TOOL
        if "engine" in cls:
            return PROVIDER_TYPE.AGENT_ENGINE
        if "agent" in cls:
            return PROVIDER_TYPE.AGENT
        if "prompt" in cls:
            return PROVIDER_TYPE.PROMPT
        if "context" in cls:
            return PROVIDER_TYPE.CONTEXT
        if "score" in cls:
            return PROVIDER_TYPE.SCORE
        if "state" in cls:
            return PROVIDER_TYPE.STATE
        if "system" in cls:
            return PROVIDER_TYPE.SYSTEM
        if "controller" in cls:
            return PROVIDER_TYPE.CONTROLLER
        if "program" in cls:
            return PROVIDER_TYPE.PROGRAM
        return PROVIDER_TYPE.UNKNOWN  # fallback

    def _compute_config_hash(self) -> Optional[str]:
        if not self.config or not getattr(self.config, "config", None):
            return None
        return hashlib.md5(json.dumps(self.config.config, sort_keys=True).encode()).hexdigest()
