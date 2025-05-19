from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.utilities.metadata.logging.log_schemas import ErrorLog, PromptGenerationLog

from ..factories.logging_provider import LoggingMixin, LoggingProvider

import json
from pathlib import Path
from app.factories.logging_provider import LogType


class PromptGeneratorBase(LoggingMixin, ABC):
    """Base class for generating prompts."""

    def __init__(self, context_provider, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)
        self.context_provider = context_provider

    def generate_prompt(self, agent_config, system_config, experiment_id, round):
        self._log.debug("Prompt generation start")
        error_message = None
        success = False
        generated_prompt = ""

        try:
            generated_prompt = self._generate_prompt(agent_config, system_config)
            success = True
            return generated_prompt
        except ValueError as ve:
            # Expected operational errors (like invalid configs)
            error_message = str(ve)
            self._log.warning("Operational prompt generation error: %s", error_message)
        except Exception as e:
            # Unexpected or critical errors
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
            self._log.error(
                "Critical prompt generation error logged: %s", error_message
            )
            raise  # re-raise critical errors explicitly
        finally:
            prompt_log = PromptGenerationLog(
                experiment_id=experiment_id,
                round=round,
                generator_name=self.__class__.__name__,
                context_provider_name=self.context_provider.__class__.__name__,
                agent_config=json.dumps(agent_config),
                system_config=json.dumps(system_config),
                generated_prompt=generated_prompt if success else "",
                success=success,
                error_message=error_message if not success else None,
                timestamp=datetime.now(timezone.utc),
            )
            self.logger.write(LogType.PROMPT_GENERATION, prompt_log)
            self._log.debug("Prompt generation logged")

    @abstractmethod
    def _generate_prompt(self, *args, **kwargs) -> str:
        """Return a generated prompt."""
        raise NotImplementedError
