from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.utilities.metadata.footer.code_annnotation_utils import split_code_and_notes
import json
from pathlib import Path
import uuid


class LintingScoreProvider(ScoreProviderBase):
    def _run(self, input: dict) -> ScoreOutputSchema:
        file_path = input["file_path"]
        session_id = input.get("session_id", self._session_id)

        # 🧠 Materialize code to disk if file_path is code content or invalid path
        if not Path(file_path).exists() or "\n" in file_path or "def " in file_path:
            temp_file = Path("experiments/snapshots") / f"{uuid.uuid4().hex}.py"
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file.write_text(file_path, encoding="utf-8")
            file_path = str(temp_file)

        file_path = Path(file_path).resolve()
        full_code = file_path.read_text(encoding="utf-8")
        clean_code, _ = split_code_and_notes(full_code)

        # Write stripped code to temp file for evaluation
        stripped_path = Path("working_files") / f"{uuid.uuid4().hex}_stripped.py"
        stripped_path.parent.mkdir(parents=True, exist_ok=True)
        stripped_path.write_text(clean_code.rstrip() + "\n", encoding="utf-8")

        # Build a dict of available tools, keyed by exactly tool.config.name.lower()
        available = {tool._config.name.lower(): tool for tool in self.tool_providers}

        def run_tool(name: str, collect_violations: bool = False):
            if name not in available:
                return 0.0, []

            try:
                raw = available[name].run({"target": str(stripped_path), "check": True}, session_id=session_id)
                parsed = raw.model_dump()
            except Exception as e:
                return 0.0, []

            score = 1.0 if parsed.get("return_code", 0) else 0.0
            if collect_violations:
                return score, parsed.get("violations", []) or []
            else:
                return score, []

        # Run each tool exactly once
        ruff_score, ruff_violations = run_tool("ruff", collect_violations=True)
        black_score, _ = run_tool("black", collect_violations=False)
        mypy_score, _ = run_tool("mypy", collect_violations=False)

        # Compute weighted score
        weighted = round(ruff_score * 0.7 + black_score * 0.2 + mypy_score * 0.1, 3)

        components = {
            "ruff": ruff_score,
            "black": black_score,
            "mypy": mypy_score
        }

        # Top Ruff Violations
        top_violations = []
        if ruff_violations:
            freq = {}
            for code in ruff_violations:
                freq[code] = freq.get(code, 0) + 1
            sorted_codes = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
            top_violations = [code for code, _ in sorted_codes[:3]]

        summary = (
            f"Top Ruff Violations: {', '.join(top_violations)}"
            if top_violations else "No Ruff violations"
        )

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.LINTING_SCORE,
            value=weighted,
            components=components,
            summary=summary
        )
