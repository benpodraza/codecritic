import json
from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema


class LintingScoreProvider(ScoreProviderBase):
    """Computes weighted linting score using injected tool providers."""

    def _run(self, input: dict) -> ScoreOutputSchema:
        file_path = input["file_path"]

        required = ["ruff", "mypy", "black", "radon"]
        available = {
            tool.__class__.__name__.lower(): tool
            for tool in getattr(self, "tool_providers", [])
        }

        # Simple normalization to lookup by config name
        resolved = {}
        for name in required:
            match = next((t for t in available.values() if name in t.__class__.__name__.lower()), None)
            if not match:
                raise ValueError(f"Missing tool provider: {name}")
            resolved[name] = match

        def parse_output(output: str, fallback_score: float = 1.0) -> float:
            try:
                result = json.loads(output)
                violations = result["stdout"].count("\n")
                return max(0.0, 1.0 - (violations / 20))
            except Exception:
                return fallback_score

        # Run each tool
        ruff_score = parse_output(resolved["ruff"].run({"target": file_path}, session_id=self._session_id))
        mypy_score = parse_output(resolved["mypy"].run({"target": file_path}, session_id=self._session_id))
        black_score = parse_output(resolved["black"].run({"target": file_path}, session_id=self._session_id))
        radon_score = parse_output(resolved["radon"].run({"target": file_path}, session_id=self._session_id))

        weighted_score = round(
            ruff_score * 0.4 +
            mypy_score * 0.3 +
            black_score * 0.2 +
            radon_score * 0.1, 3
        )

        return ScoreOutputSchema(
            name="linting_score",
            value=weighted_score,
            components={
                "ruff": ruff_score,
                "mypy": mypy_score,
                "black": black_score,
                "radon": radon_score
            }
        )
