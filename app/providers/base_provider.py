from abc import abstractmethod
from datetime import datetime, timezone
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

from app.db import init_db
from app.utilities.metadata.logging.logging_provider import LoggingMixin, LOG_TYPE
from app.db.schemas import ProviderLogSchema, ErrorLogSchema
from app.enums.logging_enums import PROVIDER_TYPE, ERROR_TYPE

class BaseProvider(LoggingMixin):
    def __init__(
        self,
        called_by_type: PROVIDER_TYPE,  
        called_by_id: int,  
        config=None,
    ) -> None:
        super().__init__()
        assert config is not None, "🚨 engine must be injected into BaseProvider"
        self._config = config
        self._engine = init_db(reset=False)
        self._called_by_type = called_by_type
        self._called_by_id = called_by_id

    def run(self, input: dict | None = None, session_id: str = "") -> str:
        input = input or {}
        if not session_id:
            raise ValueError("session_id must be provided to run()")

        self._session_id = session_id
        self._system = input.get("system", "unknown")
        self._run_id = str(uuid4())

        start_clock = time.perf_counter()
        start_time = datetime.now(timezone.utc)

        try:
            output = self._run_provider(input)
        except Exception as exc:
            latency_ms = int((time.perf_counter() - start_clock) * 1000)
            try:
                self.logger.write(
                    LOG_TYPE.ERROR,
                    ErrorLogSchema(
                        session_id=session_id,
                        error_type=self._map_error_type(exc).value,
                        message=str(exc),
                        file_path=str(Path(__file__).relative_to(Path.cwd())),
                        provider_id=self._config.id if self._config else None,
                        provider_type=self._infer_provider_type().value,
                        timestamp=start_time,
                        latency_ms=latency_ms,
                        called_by_type=self._called_by_type.value if self._called_by_type else None,
                        called_by_id=self._called_by_id,
                        run_id=self._run_id,
                    ),
                )
            except Exception:
                pass
            raise

        latency_ms = int((time.perf_counter() - start_clock) * 1000)

        try:
            input_str = json.dumps(
                {k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in input.items()},
                default=str,
            )
        except Exception:
            input_str = ""

        try:
            if hasattr(output, "model_dump"):
                dumped = output.model_dump()
                for k, v in dumped.items():
                    if isinstance(v, dict):
                        dumped[k] = json.dumps(v, default=str)
                output_str = json.dumps(dumped, default=str)
                output_schema = output.__class__.__name__
            else:
                output_str = json.dumps(output, default=str)
                output_schema = None
        except Exception:
            output_str = ""
            output_schema = None

        try:
            self.logger.write(
                LOG_TYPE.PROVIDER,
                ProviderLogSchema(
                    session_id=session_id,
                    provider_id=self._config.id if self._config else -1,
                    provider_type=self._infer_provider_type().value,
                    input=input_str,
                    output=output_str,
                    output_schema=output_schema,
                    latency_ms=latency_ms,
                    config_hash=self._compute_config_hash(),
                    file_name=getattr(self._config, "artifact_path", "").split("/")[-1]
                    if getattr(self._config, "artifact_path", None)
                    else None,
                    timestamp=start_time,
                    called_by_type=self._called_by_type if self._called_by_type else None,
                    called_by_id=self._called_by_id,
                    run_id=self._run_id,
                ),
            )
        except Exception:
            raise

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
        return PROVIDER_TYPE.UNKNOWN

    def _compute_config_hash(self) -> Optional[str]:
        if not self._config or not getattr(self._config, "config", None):
            return None
        return hashlib.md5(json.dumps(self._config.config, sort_keys=True).encode()).hexdigest()
