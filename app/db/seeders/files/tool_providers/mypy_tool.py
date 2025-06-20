import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from copy import deepcopy

from app.enums.logging_enums import RunContext
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

class MypyToolProviderV2(ToolProviderBase):
    """
    Runs `mypy` in *strict* mode and normalizes exit codes:
    0 ⇒ pass ⇒ return_code 1
    1 ⇒ type errors ⇒ return_code 0
    >1 ⇒ internal/runtime error ⇒ return_code 0 + RUNTIME_ERROR violation
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

    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        # 1) Resolve and verify via FileManager
        target_name   = input.get("target")
        resolved_type = fm.resolve_existing_filetype(target_name)
        if not fm.exists(resolved_type, target_name):
            raise FileNotFoundError(f"{target_name} not found")

        # 2) Load content from storage
        content = fm.load(resolved_type, target_name)

        # 3) Stage it in a temp file
        suffix    = Path(target_name).suffix or ".py"
        temp_path = fm.write_temp(content, suffix=suffix)

        # 4) Update context lineage
        if context:
            context       = deepcopy(context)
            context.parent_id       = self._run_id
            context.execution_chain = context.execution_chain[:] + [self._run_id]

        # 5) Build and run mypy command
        cmd = [sys.executable, "-m", "mypy", str(temp_path), *self.STRICT_ARGS]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
        except Exception as exc:
            return self._runtime_error(str(exc))

        raw_code = proc.returncode
        stdout   = (proc.stdout or "").strip()
        stderr   = (proc.stderr or "").strip()

        # 6) Normalize exit codes
        if raw_code == 0:
            return self._success(
                summary="✅ Mypy passed — no type errors",
                metrics={"error_count": 0, "raw_return_code": raw_code},
                stdout=stdout or None,
            )

        if raw_code == 1:
            violations = [line for line in stdout.splitlines() if line.strip()]
            return self._failure(
                summary=f"❌ Mypy failed with {len(violations)} error(s)",
                violations=violations,
                metrics={"error_count": len(violations), "raw_return_code": raw_code},
                stdout=stdout or None,
            )

        return self._runtime_error(stderr or stdout, raw_code)

    # ──────────────────────────────────── helpers ────────────────────────────────────
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
            summary=f"❌ Mypy execution failed: {message}",
        )
