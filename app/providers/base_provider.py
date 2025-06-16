from abc import abstractmethod
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

from app.db import init_db
from app.utilities.metadata.logging.logging_provider import LoggingMixin, LOG_TYPE, LoggingProvider
from app.db.schemas import ProviderLogSchema, ErrorLogSchema
from app.enums.logging_enums import PROVIDER_TYPE, ERROR_TYPE, RunContext

class BaseProvider:
    def __init__(
        self,
        config=None,
        context: RunContext = None,
        **kwargs
    ):
        self._config = config
        self._context = deepcopy(context) if context else None
        self._run_id = str(uuid4())
        self._engine = init_db(reset=False)
        self.logger = LoggingProvider()
        self._log = logging.getLogger(self.__class__.__name__)

        if self._context:
            if not self._context.execution_chain or self._context.execution_chain[-1] != self._run_id:
                self._context.parent_id = self._context.execution_chain[-1] if self._context.execution_chain else None
                self._context.execution_chain.append(self._run_id)
            self._session_id = self._context.session_id
            self._file_log_id = self._context.file_log_id
            self._called_by_type = self._context.called_by_type
            self._called_by_id = self._context.called_by_id
        else:
            self._session_id = None
            self._file_log_id = None
            self._called_by_type = None
            self._called_by_id = None

    def run(self, input: dict | None = None, context: RunContext = None) -> str:
        input = input or {}
        self._run_id = str(uuid4())

        if context:
            self._context = deepcopy(context)
            self._session_id     = self._context.session_id
            self._file_log_id    = self._context.file_log_id
            self._called_by_type = self._context.called_by_type
            self._called_by_id   = self._context.called_by_id
            if not self._context.execution_chain or self._context.execution_chain[-1] != self._run_id:
                self._context.parent_id = self._context.execution_chain[-1] if self._context.execution_chain else None
                self._context.execution_chain.append(self._run_id)

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
                        session_id=self._session_id,
                        file_log_id=self._file_log_id,
                        error_type=self._map_error_type(exc).value,
                        message=str(exc),
                        file_path=str(Path(__file__).relative_to(Path.cwd())),
                        provider_id=self._config.id if self._config else None,
                        provider_type=self._infer_provider_type(),
                        timestamp=start_time,
                        latency_ms=latency_ms,
                        called_by_type=self._called_by_type if self._called_by_type else None,
                        called_by_id=self._called_by_id,
                        run_id=self._run_id,
                        parent_id=self._context.parent_id if self._context else None,
                        execution_chain=self._context.execution_chain[:] if self._context else [],
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
                flat_dump = {}
                for k, v in dumped.items():
                    if isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            flat_dump[f"{k}.{sub_k}"] = sub_v
                    else:
                        flat_dump[k] = v

                output_str = json.dumps(flat_dump, default=str)
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
                    session_id=self._session_id,
                    file_log_id=self._file_log_id,
                    provider_id=self._config.id if self._config else -1,
                    provider_type=self._infer_provider_type(),
                    input=input_str,
                    output=output_str,
                    output_schema=output_schema,
                    latency_ms=latency_ms,
                    config_hash=self._compute_config_hash(getattr(self._config, "config", {})),
                    file_name=getattr(self._config, "artifact_path", "").split("/")[-1]
                    if getattr(self._config, "artifact_path", None)
                    else None,
                    timestamp=start_time,
                    called_by_type=self._called_by_type if self._called_by_type else None,
                    called_by_id=self._called_by_id,
                    run_id=self._run_id,
                    parent_id=self._context.parent_id if self._context else None,
                    execution_chain=self._context.execution_chain[:] if self._context else [],
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

    def _compute_config_hash(self, config: dict | None) -> str:
        config_str = json.dumps(config or {}, sort_keys=True)
        return hashlib.md5(config_str.encode("utf-8")).hexdigest()

    def propagate_file_log_id(self, file_log_id: str):
        self._file_log_id = file_log_id

        for attr_name in dir(self):
            attr = getattr(self, attr_name, None)

            if isinstance(attr, BaseProvider):
                attr.propagate_file_log_id(file_log_id)

            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, BaseProvider):
                        item.propagate_file_log_id(file_log_id)

            elif isinstance(attr, dict):
                for item in attr.values():
                    if isinstance(item, BaseProvider):
                        item.propagate_file_log_id(file_log_id)

    def fork_context(self) -> RunContext:
        forked = deepcopy(self._context or RunContext())
        forked.parent_id = self._run_id
        return forked
