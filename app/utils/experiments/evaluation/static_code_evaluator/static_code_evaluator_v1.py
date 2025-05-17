# app/utils/evaluation/tooling_system_evaluator.py

from typing import Optional
from app.utils.experiments.evaluation.system_evaluator import SystemEvaluator
from app.utils.tools.tool_result import ToolResult
from app.utils.agents.base_agent.tool_provider import ToolProvider


class StaticCodeEvaluator(SystemEvaluator):
    """
    SystemEvaluator implementation that scores using the ToolProvider.
    Uses pyrefactor, ruff, mypy, etc. to generate an aggregate quality score.
    """

    def __init__(self, tool_provider: ToolProvider, sonarcloud_enabled: bool = False):
        self.tool_provider = tool_provider
        self.sonarcloud_enabled = sonarcloud_enabled
        self.name = "tooling_system_evaluator"
        self.version = "v1"

    def score(self, original_code: str, modified_code: str) -> dict:
        tool_results = self.tool_provider.run_all(modified_code)

        score = 1.0
        deductions = 0.0
        metadata = {}

        for name, result in tool_results.items():
            metadata[name] = result.metadata

            if result.status != "success":
                deductions += 0.1
            if name == "pyrefactor" and "complexity" in result.metadata:
                try:
                    c = float(result.metadata["complexity"])
                    if c > 10:
                        deductions += 0.2
                except ValueError:
                    pass
            if name == "ruff" and "warnings" in result.metadata:
                try:
                    w = int(result.metadata["warnings"])
                    deductions += min(0.3, w * 0.05)
                except ValueError:
                    pass

        score = max(0.0, round(score - deductions, 2))

        return {
            "score": score,
            "tools": {k: v.output for k, v in tool_results.items()},
            "metadata": metadata,
            "evaluator_name": self.name,
            "evaluator_version": self.version
        }

    def meets_stopping_condition(self, score: dict) -> bool:
        return score.get("score", 0.0) >= 0.95
