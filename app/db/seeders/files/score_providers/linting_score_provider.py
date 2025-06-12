# app/providers/linting_score_provider_v2.py
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Dict, List, Tuple, Any

from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import ScoreOutputSchema
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.utilities.metadata.footer.code_annnotation_utils import split_code_and_notes


class LintingScoreProvider(ScoreProviderBase):
    """
    Aggregates Ruff, Black and Mypy tool scores into a single linting metric.

    Caller may supply:
        weights   – dict[str, float]   (keys: "ruff", "black", "mypy")
        threshold – float              (0‑1 range)

    Example:
        run({
            "file_path": "src/foo.py",
            "weights": {"ruff": 0.5, "black": 0.3, "mypy": 0.2},
            "threshold": 0.85
        })
    """

    # ────────────────────────────────────────────────────────────── constants
    _DEFAULT_WEIGHTS: Dict[str, float] = {"ruff": 0.7, "black": 0.2, "mypy": 0.1}
    _DEFAULT_THRESHOLD: float | None = None          # no pass / fail gating by default
    _MAX_RUFF_VIOLATIONS_CONSIDERED = 10             # for score scaling

    # ───────────────────────────────────────────────────────────── core entry
    def _run(self, input: dict) -> ScoreOutputSchema:  # noqa: D401, N802
        file_path = input["file_path"]

        # 1 ─────────────────────────────────────────── resolve & strip the code
        file_path = self._make_path_from_raw(file_path)
        full_code = file_path.read_text(encoding="utf-8")
        clean_code, _ = split_code_and_notes(full_code)

        stripped_path = self._write_working_copy(clean_code)

        # 2 ─────────────────────────────────────────────── tool execution
        available = {tp._config.name.lower(): tp for tp in self.tool_providers}
        ruff_score, ruff_violations, tool_failures = self._run_ruff(available, stripped_path)
        black_score, _ = self._run_tool("black", available, stripped_path, tool_failures)
        mypy_score, _ = self._run_tool("mypy", available, stripped_path, tool_failures)

        # 3 ─────────────────────────────────────────── weighting & threshold
        weights = self._parse_weights(input.get("weights"))
        weighted_score = round(
            ruff_score * weights["ruff"]
            + black_score * weights["black"]
            + mypy_score * weights["mypy"],
            3,
        )

        threshold = input.get("threshold", self._DEFAULT_THRESHOLD)
        meets_threshold = (threshold is None) or (weighted_score >= threshold)

        # 4 ───────────────────────────────────────────── components / summary
        components: Dict[str, float] = {
            "ruff_score": ruff_score,
            "ruff_violations": float(len(ruff_violations)),
            "black_score": black_score,
            "mypy_score": mypy_score,
            "tool_failure_count": float(len(tool_failures)),
            "weight_ruff": weights["ruff"],
            "weight_black": weights["black"],
            "weight_mypy": weights["mypy"],
        }
        if threshold is not None:
            components["threshold"] = threshold
            components["meets_threshold"] = 1.0 if meets_threshold else 0.0

        summary = self._build_summary(
            ruff_violations=ruff_violations,
            tool_failures=tool_failures,
            meets_threshold=meets_threshold,
            threshold=threshold,
        )

        return ScoreOutputSchema(
            name=SCORING_METRIC_TYPE.LINTING_SCORE,
            value=weighted_score,
            components=components,
            summary=summary,
        )

    # ───────────────────────────────────────────────────────────── helpers
    # 1️⃣  FILE‑HANDLING ---------------------------------------------------
    def _make_path_from_raw(self, maybe_code: str) -> Path:
        """Create a temp file if the input is *code*, otherwise treat it as a path."""
        if Path(maybe_code).exists() and "\n" not in maybe_code:
            return Path(maybe_code).resolve()

        tmp = Path("experiments/snapshots") / f"{uuid.uuid4().hex}.py"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(maybe_code, encoding="utf‑8")
        print(f"📄  Created temp file for raw code: {tmp}")
        return tmp.resolve()

    def _write_working_copy(self, clean_code: str) -> Path:
        stripped = Path("working_files") / f"{uuid.uuid4().hex}_stripped.py"
        stripped.parent.mkdir(parents=True, exist_ok=True)
        stripped.write_text(clean_code.rstrip() + "\n", encoding="utf‑8")
        return stripped.resolve()

    # 2️⃣  TOOL RUNNERS ----------------------------------------------------
    def _run_ruff(
        self,
        available: Dict[str, Any],
        target_path: Path,
    ) -> Tuple[float, List[str], Dict[str, str]]:
        """Runs Ruff and returns (score, violations, failures‑dict)."""
        tool_failures: Dict[str, str] = {}

        score, violations = self._run_tool(
            "ruff", available, target_path, tool_failures, collect_violations=True
        )

        # Ruff score: scaled linearly down by violation count, capped at 10+
        score = 1.0 - min(1.0, len(violations) / self._MAX_RUFF_VIOLATIONS_CONSIDERED)
        return score, violations, tool_failures


    def _run_tool(
        self,
        name: str,
        available: Dict[str, Any],
        target_path: Path,
        failures: Dict[str, str],
        collect_violations: bool = False,
    ) -> Tuple[float, List[str]]:
        """
        Returns a score in [0, 1] based on violation count if tool succeeded,
        or 0.0 if the tool failed (e.g., crashed or missing).
        """
        if name not in available:
            failures[name] = "not_available"
            return 0.0, []

        try:
            result = available[name].run({"target": str(target_path), "check": True})
        except Exception as exc:
            failures[name] = f"crashed: {exc}"
            return 0.0, []

        # Always try to extract violations
        violations = getattr(result, "violations", []) or []
        rc = getattr(result, "return_code", 0)

        # Only fail hard if the tool couldn't run
        if rc not in {0, 1} and not violations:
            failures[name] = result.summary or "failed"
            return (0.0, []) if not collect_violations else (0.0, violations)

        # Compute score based on violation count
        count = len(violations)
        if name == "ruff":
            score = 1.0  # Ruff handled in _run_ruff
        else:
            score = 1.0 - min(1.0, 0.1 * count)

        return (score, violations) if collect_violations else (score, [])


    # 3️⃣  WEIGHT PARSING --------------------------------------------------
    def _parse_weights(self, custom: Dict[str, float] | None) -> Dict[str, float]:
        weights = {**self._DEFAULT_WEIGHTS}

        if custom:
            weights.update(
                {k.lower(): float(v) for k, v in custom.items() if k.lower() in weights}
            )

        total = sum(weights.values()) or 1.0
        return {k: v / total for k, v in weights.items()}

    # 4️⃣  SUMMARY BUILDER --------------------------------------------------
    def _build_summary(
        self,
        *,
        ruff_violations: List[str],
        tool_failures: Dict[str, str],
        meets_threshold: bool,
        threshold: float | None,
    ) -> str:
        lines: List[str] = []

        if ruff_violations:
            top_codes = {}
            for code in ruff_violations:
                top_codes[code] = top_codes.get(code, 0) + 1
            top_sorted = sorted(top_codes.items(), key=lambda kv: kv[1], reverse=True)
            lines.append(
                "Top Ruff violations: "
                + ", ".join(f"{c}×{n}" for c, n in top_sorted[:3])
            )
        else:
            lines.append("No Ruff violations detected")

        if tool_failures:
            lines.append("⚠️  Tool failures: " + ", ".join(tool_failures))

        if threshold is not None:
            state = "✅ meets" if meets_threshold else "❌ below"
            lines.append(f"{state} threshold {threshold:.2f}")

        return "\n".join(lines)
