from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
import json

class LintingScoreProvider(ScoreProviderBase):
    def _run(self, input: dict) -> ScoreOutputSchema:
        file_path = input["file_path"]
        session_id = input.get("session_id", self._session_id)
        available = {tool.config.name.lower(): tool for tool in self.tool_providers}

        def safe_score(name):
            try:
                result = available[name].run({"target": file_path}, session_id=session_id)
                return float(json.loads(result).get("score", 0.0))
            except Exception:
                return 0.0

        def safe_violations(name):
            try:
                result = available[name].run({"target": file_path}, session_id=session_id)
                return json.loads(result).get("violations", [])
            except Exception:
                return []

        ruff_score = safe_score("ruff")
        ruff_codes = safe_violations("ruff")
        black_score = safe_score("black")
        mypy_score = safe_score("mypy")

        weighted_score = round(
            ruff_score * 0.7 +
            black_score * 0.2 +
            mypy_score * 0.1, 3
        )

        components = {
            "ruff": ruff_score,
            "black": black_score,
            "mypy": mypy_score
        }

        top_violations = sorted(set(ruff_codes), key=ruff_codes.count, reverse=True)[:3]
        self._log.debug(f"Top Ruff Violations: {top_violations}")

        return ScoreOutputSchema(
            name="linting_score",
            value=weighted_score,
            components=components
        )
