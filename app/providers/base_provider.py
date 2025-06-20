from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import logging
import time
import random
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4
import traceback

from app.db import init_db
from app.utilities.metadata.logging.logging_provider import LoggingMixin, LOG_TYPE, LoggingProvider
from app.db.schemas import ProviderLogSchema, ErrorLogSchema
from app.enums.logging_enums import PROVIDER_TYPE, ERROR_TYPE, RunContext

DEFAULT_MAX_RETRIES = 2
DEFAULT_BACKOFF_SECONDS = 0.25

class BaseProvider(ABC):
    def __init__(self, config=None, context: RunContext = None, **kwargs):
        self._config = config
        self._context = deepcopy(context) if context else None
        self._run_id = str(uuid4())
        self._engine = init_db(reset=False)
        self.logger = LoggingProvider()
        self._log = logging.getLogger(self.__class__.__name__)
        self._provider_type = getattr(config, "provider_type", PROVIDER_TYPE.UNKNOWN)

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

    def run(self, input: dict | None = None, context: RunContext = None, **kwargs) -> str:
        input = input or {}
        max_retries = input.get("max_retries", DEFAULT_MAX_RETRIES)
        backoff_seconds = input.get("backoff_seconds", DEFAULT_BACKOFF_SECONDS)
        retryable = {
            ERROR_TYPE.CONNECTION,
            ERROR_TYPE.TIMEOUT,
            ERROR_TYPE.UNKNOWN,
        }

        if context:
            self._context = deepcopy(context)
            self._session_id     = self._context.session_id
            self._file_log_id    = self._context.file_log_id
            self._called_by_type = self._context.called_by_type
            self._called_by_id   = self._context.called_by_id

        for attempt in range(max_retries + 1):
            try:
                local_input = input.copy()
            except Exception as e:
                traceback.print_exc()
                raise

            local_input["retry_count"] = attempt
            self._run_id = str(uuid4())

            if self._context:
                if not self._context.execution_chain or self._context.execution_chain[-1] != self._run_id:
                    self._context.parent_id = self._context.execution_chain[-1] if self._context.execution_chain else None
                    self._context.execution_chain.append(self._run_id)

            start_time = datetime.now(timezone.utc)
            start_clock = time.perf_counter()

            try:
                output = self._run_provider(local_input, **kwargs)
                break
            except Exception as exc:
                latency_ms = int((time.perf_counter() - start_clock) * 1000)
                err_type = self._map_error_type(exc)

                try:
                    self.logger.write(
                        LOG_TYPE.ERROR,
                        ErrorLogSchema(
                            session_id=self._session_id,
                            file_log_id=self._file_log_id,
                            error_type=err_type.value,
                            message=str(exc),
                            file_path=local_input.get("file_path"),
                            provider_id=self._config.id if self._config else None,
                            provider_type=self._provider_type,
                            timestamp=start_time,
                            latency_ms=latency_ms,
                            called_by_type=self._called_by_type,
                            called_by_id=self._called_by_id,
                            run_id=self._run_id,
                            parent_id=self._context.parent_id if self._context else None,
                            execution_chain=(self._context.execution_chain[:] if self._context else []),
                        ),
                    )
                except Exception:
                    traceback.print_exc()

                if attempt == max_retries or err_type not in retryable:
                    raise

                sleep_time = backoff_seconds * (2 ** attempt) + random.uniform(0, backoff_seconds)
                time.sleep(sleep_time)

        latency_ms = int((time.perf_counter() - start_clock) * 1000)

        try:
            input_str = json.dumps({k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in input.items()}, default=str)
        except Exception:
            input_str = ""

        try:
            if hasattr(output, "model_dump"):
                output_str = json.dumps(output.model_dump(), default=str)
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
                    provider_type=self._provider_type,
                    input=input_str,
                    output=output_str,
                    output_schema=output_schema,
                    latency_ms=latency_ms,
                    config_hash=self._compute_config_hash(getattr(self._config, "config", {})),
                    file_name=str(input.get("file_path")) if "file_path" in input else None,
                    timestamp=start_time,
                    called_by_type=self._called_by_type,
                    called_by_id=self._called_by_id,
                    run_id=self._run_id,
                    parent_id=self._context.parent_id if self._context else None,
                    execution_chain=(self._context.execution_chain[:] if self._context else []),
                ),
            )
        except Exception:
            traceback.print_exc()
            raise

        return output

    def _map_error_type(self, exc: Exception) -> ERROR_TYPE:
        msg = str(exc).lower()
        if "timeout" in msg or "timed out" in msg:
            return ERROR_TYPE.TIMEOUT
        elif "auth" in msg or "unauthorized" in msg or "forbidden" in msg:
            return ERROR_TYPE.AUTHENTICATION
        elif "connect" in msg or "unreachable" in msg or "network" in msg:
            return ERROR_TYPE.CONNECTION
        elif "config" in msg or "invalid argument" in msg:
            return ERROR_TYPE.CONFIGURATION
        elif "validation" in msg or "schema" in msg:
            return ERROR_TYPE.VALIDATION
        elif "runtime" in msg or "execution failed" in msg:
            return ERROR_TYPE.RUNTIME
        return ERROR_TYPE.UNKNOWN

    def _compute_config_hash(self, config: dict | None) -> str:
        config = config or {}
        components = config.get("components", {})
        config_str = json.dumps(components, sort_keys=True)
        return hashlib.md5(config_str.encode("utf-8")).hexdigest()

    def fork_context(self) -> RunContext:
        forked = deepcopy(self._context or RunContext())
        forked.parent_id = self._run_id
        forked.called_by_type = self._provider_type
        forked.called_by_id = getattr(self._config, "id", None)
        return forked

    @abstractmethod
    def _run_provider(self, input: dict, **kwargs):
        ...
