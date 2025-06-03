from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
from app.enums.scoring_enums import SCORING_METRIC_TYPE
import json


class LintingScoreProvider(ScoreProviderBase):
    def _run(self, input: dict) -> ScoreOutputSchema:
        file_path = input["file_path"]
        session_id = input.get("session_id", self._session_id)

        # Build a dict of available tools, keyed by exactly tool.config.name.lower()
        available = {tool._config.name.lower(): tool for tool in self.tool_providers}

        # DEBUG / DIAGNOSTICS: print or log which tools are actually registered
        print("Available linting tools:", list(available.keys()))

        def run_tool(name: str, collect_violations: bool = False):
            """
            - name: lowercase tool name (must match tool.config.name.lower())
            - collect_violations: if True, return list of violations as second element
            Returns:
              (score: float, violations: list[str])
            """
            if name not in available:
                # Tool wasn’t registered; treat that as a zero score
                print(f"  → Tool '{name}' not found among: {list(available.keys())}")
                return 0.0, []

            try:
                raw = available[name].run({"target": file_path, "check": True}, session_id=session_id)
                parsed = json.loads(raw)
            except Exception as e:
                print(f"  → Exception running '{name}': {e}")
                return 0.0, []

            # parsed.get("return_code") will be 1 on pass, 0 on fail
            score = 1.0 if parsed.get("return_code", 0) else 0.0

            if collect_violations:
                # parsed["violations"] should be a list[str] if check mode fails
                return score, parsed.get("violations", []) or []
            else:
                return score, []

        # Run each tool exactly once
        ruff_score, ruff_violations = run_tool("ruff", collect_violations=True)
        black_score, _ = run_tool("black", collect_violations=False)
        mypy_score, _ = run_tool("mypy", collect_violations=False)

        # Now compute weighted score
        weighted = round(ruff_score * 0.7 + black_score * 0.2 + mypy_score * 0.1, 3)

        components = {
            "ruff": ruff_score,
            "black": black_score,
            "mypy": mypy_score
        }

        # Pick top‐3 most frequent Ruff violation codes, if any
        top_violations = []
        if ruff_violations:
            # e.g. ruff_violations = ["F401", "E501", "F401", ...]
            freq = {}
            for code in ruff_violations:
                freq[code] = freq.get(code, 0) + 1
            # sort descending by count
            sorted_codes = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
            top_violations = [code for code, _ in sorted_codes[:3]]

        summary = (
            f"Top Ruff Violations: {', '.join(top_violations)}"
            if top_violations
            else "No Ruff violations"
        )

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.LINTING_SCORE,
            value=weighted,
            components=components,
            summary=summary
        )
