# app/providers/ruff_tool_provider_v2.py
import subprocess
import json
from typing import Any, Dict, List, Optional
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema


class RuffToolProviderV2(ToolProviderBase):
    """
    Executes `ruff check --output-format json` and normalises results so that
    return_code 1 ⇒ pass, 0 ⇒ any violation or runtime error.
    """

    def _run(self, input: dict) -> ToolOutputSchema:  # noqa: D401, N802
        target: str = input.get("target")
        cmd = ["ruff", "check", "--output-format", "json", target]

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf‑8", errors="ignore"
            )
        except Exception as exc:
            return self._runtime_error(str(exc))

        raw_code = proc.returncode
        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()

        # ───────────────────────────────────────────── parse Ruff JSON (if any)
        try:
            parsed = json.loads(stdout or "[]")
            violations: List[str] = [
                v["code"]
                for file_item in parsed
                for v in file_item.get("violations", [])
            ]
        except json.JSONDecodeError:
            # JSON decode failure = runtime problem
            return self._runtime_error("Failed to parse Ruff JSON output", raw_code)

        violation_count = len(violations)

        # ───────────────────────────────────────────────────────── outcome map
        if raw_code == 0:  # Ruff found zero violations
            return self._success(
                summary="✅ Ruff passed — no violations",
                metrics={
                    "violation_count": 0,
                    "raw_return_code": raw_code,
                },
            )

        if raw_code == 1:  # Ruff found violations
            return self._failure(
                summary=f"❌ Ruff failed with {violation_count} violation(s)",
                violations=violations or ["UNKNOWN_VIOLATION"],
                metrics={
                    "violation_count": violation_count,
                    "raw_return_code": raw_code,
                },
                stdout=stdout or None,
            )

        # Anything else → runtime error
        return self._runtime_error(stderr or stdout, raw_code)

    # ────────────────────────────────────────────────────────────── helpers
    def _success(
        self,
        summary: str,
        metrics: Dict[str, Any],
    ) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=1,
            stdout=None,
            stderr=None,
            violations=None,
            metrics=metrics,
            summary=summary,
        )

    def _failure(
        self,
        summary: str,
        violations: List[str],
        metrics: Dict[str, Any],
        stdout: Optional[str] = None,
    ) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=0,
            stdout=stdout,
            stderr=None,
            violations=violations,
            metrics=metrics,
            summary=summary,
        )

    def _runtime_error(self, message: str, raw_code: int | None = None) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=0,
            stdout=None,
            stderr=message,
            violations=["RUNTIME_ERROR"],
            metrics={"raw_return_code": raw_code, "exception": 1},
            summary=f"❌ Ruff execution failed: {message}",
        )
