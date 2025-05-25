from typing import Dict
from app.providers.score_provider_base import ScoreProviderBase
import json

class LintScoreProvider(ScoreProviderBase):
    def _run(self, input: dict) -> str:
        source_code = input["source_code"]
        file_path = input["file_path"]
        experiment_id = input["session_id"]

        tool_results = {
            name: provider.run({"target": file_path, "session_id": experiment_id})
            for name, provider in self.tool_providers.items()
        }

        total_lines = source_code.count("\n") + 1

        formatted_lines = total_lines
        if "BlackToolProvider" in tool_results:
            formatted_lines = total_lines - len(
                tool_results["BlackToolProvider"].stdout.strip().splitlines()
            )

        lint_errors = len(tool_results["RuffToolProvider"].stdout.strip().splitlines()) if "RuffToolProvider" in tool_results else 0
        type_errors = len(tool_results["MypyToolProvider"].stdout.strip().splitlines()) if "MypyToolProvider" in tool_results else 0

        complexity = maintainability = 0.0
        if "RadonToolProvider" in tool_results:
            radon_output = tool_results["RadonToolProvider"].stdout.strip()
            complexity, maintainability = self._parse_radon_output(radon_output)

        scores = {
            "formatting_compliance": (formatted_lines / total_lines) * 100,
            "lint_error_count": lint_errors,
            "type_error_count": type_errors,
            "average_complexity": complexity,
            "maintainability_index": maintainability,
        }

        return json.dumps(scores)

    def _parse_radon_output(self, output: str) -> tuple[float, float]:
        return 0.0, 0.0  # stub for now
