from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from ...abstract_classes.agent_base import AgentBase
from ...enums.agent_enums import AgentRole
from ...factories.logging_provider import (
    CodeQualityLog,
    ConversationLog,
    ErrorLog,
    LoggingProvider,
    FeedbackLog,
)
from ...factories.tool_provider import ToolProviderFactory
from ...utilities.snapshots.snapshot_writer import SnapshotWriter
from .evaluator_agent import _analyze_radon


class PatchAgent(AgentBase):
    """Apply mediator recommendations as code patches."""

    def __init__(
        self,
        target: str,
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
    ) -> None:
        super().__init__(logger)
        self.target = target
        self.snapshot_writer = snapshot_writer or SnapshotWriter()
        self.black = ToolProviderFactory.create("black")
        self.ruff = ToolProviderFactory.create("ruff")
        self.mypy = ToolProviderFactory.create("mypy")
        self.conversation_logs: List[ConversationLog] = []
        self.error_logs: List[ErrorLog] = []
        self.quality_logs: List[CodeQualityLog] = []

    def _apply_patch(self, code: str, op: dict[str, Any]) -> str:
        if op.get("op") == "replace":
            old = op.get("from", "")
            new = op.get("to", "")
            if old not in code:
                raise ValueError(f"pattern '{old}' not found")
            return code.replace(old, new)
        if op.get("op") == "append":
            return code + op.get("text", "")
        raise ValueError(f"unsupported op: {op.get('op')}")

    def _run_agent_logic(self, *args, **kwargs) -> None:  # noqa: C901 - small
        feedback = kwargs.get("feedback")
        if feedback:
            for item in feedback:
                self.log_feedback(
                    FeedbackLog(
                        experiment_id="exp",
                        round=0,
                        source="patch",
                        feedback=str(item),
                    )
                )

        recs: List[ConversationLog] | None = kwargs.get("recommendations")
        if not recs:
            return
        path = Path(self.target)
        before = path.read_text(encoding="utf-8")
        after = before
        for conv in recs:
            self.conversation_logs.append(conv)
            try:
                ops = json.loads(conv.content)
            except json.JSONDecodeError as exc:
                err = ErrorLog(
                    experiment_id="exp",
                    round=0,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    file_path=self.target,
                )
                self.error_logs.append(err)
                self.log_error(err)
                continue
            self.log_conversation(conv)
            for op in ops:
                try:
                    after = self._apply_patch(after, op)
                except Exception as exc:  # patch failure
                    err = ErrorLog(
                        experiment_id="exp",
                        round=0,
                        error_type=type(exc).__name__,
                        message=str(exc),
                        file_path=self.target,
                    )
                    self.error_logs.append(err)
                    self.log_error(err)
        path.write_text(after, encoding="utf-8")
        try:
            self.black.run(self.target)
            self.ruff.run(self.target)
            self.mypy.run(self.target)
        except Exception as exc:  # pragma: no cover - tool failure
            err = ErrorLog(
                experiment_id="exp",
                round=0,
                error_type=type(exc).__name__,
                message=str(exc),
                file_path=self.target,
            )
            self.error_logs.append(err)
            self.log_error(err)
        final = path.read_text(encoding="utf-8")
        complexity, maintainability = _analyze_radon(final)
        quality = CodeQualityLog(
            experiment_id="exp",
            round=0,
            symbol=self.target,
            lines_of_code=len(final.splitlines()),
            cyclomatic_complexity=complexity,
            maintainability_index=maintainability,
            lint_errors=0,
        )
        self.quality_logs.append(quality)
        self.log_code_quality(quality)
        for err in self.error_logs:
            self.log_error(err)
        self.snapshot_writer.write_snapshot(
            experiment_id="exp",
            round=0,
            file_path=self.target,
            before=before,
            after=final,
            symbol=self.target,
            agent_role=AgentRole.PATCHER,
        )
