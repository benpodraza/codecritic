from __future__ import annotations

from typing import List
from datetime import datetime, timezone
from pathlib import Path

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...factories.tool_provider import ToolProviderFactory
from ...factories.logging_provider import (
    ErrorLog,
    PromptLog,
    LoggingProvider,
    FeedbackLog,
)
from ...utilities.snapshots.snapshot_writer import SnapshotWriter


class GeneratorAgent(AgentBase):
    """Agent responsible for formatting code using black."""

    def __init__(
        self,
        target: str,
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
    ) -> None:
        super().__init__(logger)
        self.target = target
        self.formatter = ToolProviderFactory.create("black")
        self.docformatter = ToolProviderFactory.create("docformatter")
        self.prompt_logs: List[PromptLog] = []
        self.error_logs: List[ErrorLog] = []
        self.snapshot_writer = snapshot_writer or SnapshotWriter()

    def _run_agent_logic(self, *args, **kwargs) -> None:
        feedback = kwargs.get("feedback")
        if feedback:
            for item in feedback:
                self.log_feedback(
                    FeedbackLog(
                        experiment_id="exp",
                        round=0,
                        source="generator",
                        feedback=str(item),
                    )
                )
        before = Path(self.target).read_text(encoding="utf-8")
        log = PromptLog(
            experiment_id="exp",
            round=0,
            system="system",
            agent_id="generator",
            agent_role=AgentRole.GENERATOR,
            symbol=self.target,
            prompt="format code",
            response=None,
            attempt_number=0,
            agent_action_outcome="started",
        )
        self.prompt_logs.append(log)
        try:
            self.formatter.run(self.target)
            self.docformatter.run(self.target)
            log.agent_action_outcome = "success"
            self._log.info("Formatted %s", self.target)
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
            self._log.exception("Formatting failed for %s", self.target)
        finally:
            log.stop = datetime.now(timezone.utc)
            after = Path(self.target).read_text(encoding="utf-8")
            self.snapshot_writer.write_snapshot(
                experiment_id="exp",
                round=0,
                file_path=self.target,
                before=before,
                after=after,
                symbol=self.target,
                agent_role=AgentRole.GENERATOR,
            )
            self.log_prompt(log)
            for err in self.error_logs:
                self.log_error(err)
