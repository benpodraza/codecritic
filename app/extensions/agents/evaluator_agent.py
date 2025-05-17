from __future__ import annotations
from typing import List
from ...abstract_classes.agent_base import AgentBase
from ...factories.tool_provider import ToolProviderFactory
from ...utilities.metadata.logging import CodeQualityLog, ErrorLog

class EvaluatorAgent(AgentBase):
    def __init__(self, target: str) -> None:
        super().__init__()
        self.target = target
        self.mypy = ToolProviderFactory.create("mypy")
        self.ruff = ToolProviderFactory.create("ruff")
        self.radon = ToolProviderFactory.create("radon")
        self.quality_logs: List[CodeQualityLog] = []
        self.error_logs: List[ErrorLog] = []

    def _run_agent_logic(self, *args, **kwargs) -> None:
        complexity = 0.0
        try:
            self.mypy.run(self.target)
            ruff_proc = self.ruff.run(self.target)
            
            # Handle radon as parsed JSON output
            radon_result = self.radon.run(self.target)
            complexity = sum(item["complexity"] for item in radon_result) / len(radon_result) if radon_result else 0.0

        except Exception as exc:
            self.logger.warning("Radon unavailable: %s", exc)

        lines = sum(1 for _ in open(self.target, "r", encoding='utf-8'))
        log = CodeQualityLog(
            experiment_id="exp",
            round=0,
            symbol=self.target,
            lines_of_code=lines,
            cyclomatic_complexity=complexity,
            maintainability_index=0.0,
            lint_errors=0 if ruff_proc.returncode == 0 else 1,
        )
        self.quality_logs.append(log)
