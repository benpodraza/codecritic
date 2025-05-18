from __future__ import annotations

from typing import List
from datetime import datetime, timezone

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...factories.tool_provider import ToolProviderFactory
from ...utilities.metadata.logging import ErrorLog, PromptLog


class GeneratorAgent(AgentBase):
    """Agent responsible for formatting code using black."""

    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target
        self.formatter = ToolProviderFactory.create("black")
        self.prompt_logs: List[PromptLog] = []
        self.error_logs: List[ErrorLog] = []

    def _run_agent_logic(self, *args, **kwargs) -> None:
        log = PromptLog(
            experiment_id="exp",
            round=0,
            system="system",
            agent_id="generator",
            agent_role=AgentRole.GENERATOR.value,
            symbol=self.target,
            prompt="format code",
            response=None,
            attempt_number=0,
            agent_action_outcome="started",
        )
        self.prompt_logs.append(log)
        try:
            self.formatter.run(self.target)
            log.agent_action_outcome = "success"
            self.logger.info("Formatted %s", self.target)
        except Exception as exc:
            log.agent_action_outcome = "error"
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.logger.exception("Formatting failed for %s", self.target)
        finally:
            log.stop = datetime.now(timezone.utc)
