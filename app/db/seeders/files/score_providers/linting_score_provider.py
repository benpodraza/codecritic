import json
from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
from app.factories.tool_provider_factory import ToolProviderFactory

class LintingScoreProvider(ScoreProviderBase):
    """Instantiates tool providers by ID and computes weighted linting score."""

    def _run(self, input: dict) -> ScoreOutputSchema:
        file_path = input["file_path"]
        tool_ids = self.config.config.get("tool_ids", {})

        required = ["ruff", "mypy", "black", "radon"]
        missing = [k for k in required if k not in tool_ids]
        if missing:
            raise ValueError(f"Missing required tool IDs in config: {missing}")

        # Load providers
        tool_providers = {
            name: ToolProviderFactory.create(tool_id)
            for name, tool_id in tool_ids.items()
        }

        # Helper to extract violation count
        def parse_output(output: str, fallback_score: float = 1.0) -> float:
            try:
                result = json.loads(output)
                violations = result["stdout"].count("\n")
                return max(0.0, 1.0 - (violations / 20))  # normalize: 0–1
            except Exception:
                return fallback_score  # If result can't be parsed, assume OK

        # Run and parse scores
        ruff_raw = tool_providers["ruff"].run({"target": file_path}, session_id=self._session_id)
        ruff_score = parse_output(ruff_raw)

        mypy_raw = tool_providers["mypy"].run({"target": file_path}, session_id=self._session_id)
        mypy_score = parse_output(mypy_raw)

        black_raw = tool_providers["black"].run({"target": file_path}, session_id=self._session_id)
        black_score = parse_output(black_raw)

        radon_raw = tool_providers["radon"].run({"target": file_path}, session_id=self._session_id)
        radon_score = parse_output(radon_raw)

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
