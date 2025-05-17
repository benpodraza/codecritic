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
            radon_proc = self.radon.run(self.target)

            # Parse "Complexity: X.Y" from radon output
            for line in radon_proc.stdout.splitlines():
                if "Complexity:" in line:
                    try:
                        complexity = float(line.split("Complexity:")[1].strip())
                    except ValueError:
                        pass
                    break

        except Exception as exc:
            self.logger.warning("Radon unavailable: %s", exc)

        lines = sum(1 for _ in open(self.target, "r", encoding="utf-8"))
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
