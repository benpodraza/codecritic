# app/providers/mypy_tool_provider_v2.py
import subprocess
import sys
from typing import Any, Dict, List, Optional
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema


class MypyToolProviderV2(ToolProviderBase):
    """
    Runs `mypy` in *strict* mode and normalises exit‑codes:
    0 ⇒ pass ⇒ return_code 1
    1 ⇒ type errors ⇒ return_code 0
    >1 ⇒ internal / runtime error ⇒ return_code 0 + RUNTIME_ERROR violation
    """

    STRICT_ARGS: list[str] = [
        "--strict",
        "--disallow-untyped-defs",
        "--disallow-incomplete-defs",
        "--disallow-untyped-calls",
        "--disallow-untyped-decorators",
        "--disallow-any-generics",
        "--warn-unused-ignores",
        "--warn-return-any",
        "--no-implicit-optional",
        "--strict-equality",
    ]

    def _run(self, input: dict) -> ToolOutputSchema:  # noqa: D401, N802
        target: str = input.get("target")

        cmd = [sys.executable, "-m", "mypy", target, *self.STRICT_ARGS]

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf‑8", errors="ignore"
            )
        except Exception as exc:
            return self._runtime_error(str(exc))

        raw_code = proc.returncode
        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()

        # ───────────────────────────────────────────────────────── parse outcome
        if raw_code == 0:
            return self._success(
                summary="✅ Mypy passed — no type errors",
                metrics={"error_count": 0, "raw_return_code": raw_code},
                stdout=stdout or None,
            )

        if raw_code == 1:
            violations = [line for line in stdout.splitlines() if line.strip()]
            return self._failure(
                summary=f"❌ Mypy failed with {len(violations)} error(s)",
                violations=violations,
                metrics={
                    "error_count": len(violations),
                    "raw_return_code": raw_code,
                },
                stdout=stdout or None,
            )

        # raw_code > 1 → mypy internal error
        return self._runtime_error(stderr or stdout, raw_code)

    # ────────────────────────────────────────────────────────────── helpers
    def _success(
        self,
        summary: str,
        metrics: Dict[str, Any],
        stdout: Optional[str] = None,
    ) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=1,
            stdout=stdout,
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
            summary=f"❌ Mypy execution failed: {message}",
        )
