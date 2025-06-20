from __future__ import annotations

from copy import deepcopy
import uuid
from typing import Dict, List, Tuple, Any

from app.enums.logging_enums import RunContext
from app.providers.score_provider_base import ScoreProviderBase
from app.db.schemas import (
    LintingScoreConfig,
    ScoreOutputSchema,
    LintingScoreComponents
)
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.utilities.metadata.footer.code_annnotation_utils import split_content_and_notes
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

class LintingScoreProvider(ScoreProviderBase):
    ConfigSchema = LintingScoreConfig 
    _DEFAULT_WEIGHTS: Dict[str, float] = {"ruff": 0.7, "black": 0.2, "mypy": 0.1}
    _DEFAULT_THRESHOLD: float | None = None
    _MAX_RUFF_VIOLATIONS_CONSIDERED = 10

    def _run(self, input: dict, context: RunContext | None = None) -> ScoreOutputSchema:
        stripped_filename = None

        try:
            file_path = input.get("file_path")
            if not file_path or not isinstance(file_path, str):
                raise ValueError("❌ 'file_path' is required and must be a non-empty string.")

            ftype = fm.resolve_existing_filetype(file_path)
            full_code = fm.load(ftype, file_path)
            clean_code, _ = split_content_and_notes(full_code)

            stripped_filename = self._write_working_copy(clean_code)

            available = {tp._config.name.lower(): tp for tp in self.tool_providers}

            ruff_score, ruff_violations, tool_failures = self._run_ruff(
                available, stripped_filename, context
            )
            black_score, black_violations = self._run_tool(
                "black", available, stripped_filename, tool_failures, context,
                collect_violations=True
            )
            mypy_score, mypy_violations = self._run_tool(
                "mypy", available, stripped_filename, tool_failures, context,
                collect_violations=True
            )

            weights = self._parse_weights(input.get("weights"))
            weighted_score = round(
                ruff_score * weights["ruff"]
                + black_score * weights["black"]
                + mypy_score * weights["mypy"],
                3,
            )

            threshold = input.get("threshold", self._DEFAULT_THRESHOLD)
            meets_threshold = (threshold is None) or (weighted_score >= threshold)

            components = LintingScoreComponents(
                type="linting",
                ruff_score=ruff_score,
                ruff_violations=ruff_violations,
                black_score=black_score,
                black_violations=black_violations,
                mypy_score=mypy_score,
                mypy_violations=mypy_violations,
                tool_failure_count=len(tool_failures),
                weight_ruff=weights["ruff"],
                weight_black=weights["black"],
                weight_mypy=weights["mypy"],
            )

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

        finally:
            if stripped_filename:
                fm.delete(FILETYPE.WORKING, stripped_filename)


    def _write_working_copy(self, clean_code: str) -> str:
        name = f"{uuid.uuid4().hex}_stripped.py"
        fm.save(FILETYPE.WORKING, name, clean_code.rstrip() + "\n")
        return name


    def _run_ruff(
        self,
        available: Dict[str, Any],
        target_filename: str,
        context: RunContext | None,
    ) -> Tuple[float, List[str], Dict[str, str]]:
        score, violations = self._run_tool_with_context(
            tool=available.get("ruff"),
            input={"target": target_filename, "check": True},
            context=context,
            collect_violations=True,
        ) if "ruff" in available else (0.0, [])
        ruff_score = 1.0 - min(1.0, len(violations) / self._MAX_RUFF_VIOLATIONS_CONSIDERED)
        return ruff_score, violations, {}


    def _run_tool(
        self,
        name: str,
        available: Dict[str, Any],
        target_filename: str,
        failures: Dict[str, str],
        context: RunContext | None,
        collect_violations: bool = False
    ) -> Tuple[float, List[str]]:
        tool = available.get(name)
        if not tool:
            failures[name] = "not_available"
            return 0.0, []

        try:
            score, violations = self._run_tool_with_context(
                tool=tool,
                input={"target": target_filename, "check": True},
                context=context,
                collect_violations=collect_violations,
            )
        except Exception as exc:
            failures[name] = f"crashed: {exc}"
            return 0.0, []

        if score == 0.0 and not violations:
            failures[name] = "failed or no output"
            return (0.0, []) if not collect_violations else (0.0, violations)

        return (score, violations) if collect_violations else (score, [])


    def _run_tool_with_context(
        self,
        tool,
        input: dict,
        context: RunContext | None = None,
        collect_violations: bool = False
    ) -> Tuple[float, List[str]]:
        ctx = self.fork_context()
        result = tool.run(input=input, context=ctx)

        violations = getattr(result, "violations", []) or []
        rc = getattr(result, "return_code", 0)

        if rc not in {0, 1} and not violations:
            return 0.0, violations

        count = len(violations)
        score = 1.0 - min(1.0, 0.1 * count)
        return (score, violations) if collect_violations else (score, [])


    def _parse_weights(self, custom: Dict[str, float] | None) -> Dict[str, float]:
        weights = {**self._DEFAULT_WEIGHTS}
        if custom:
            weights.update(
                {k.lower(): float(v) for k, v in custom.items() if k.lower() in weights}
            )
        total = sum(weights.values()) or 1.0
        return {k: v / total for k, v in weights.items()}


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
            top_codes: Dict[str, int] = {}
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
