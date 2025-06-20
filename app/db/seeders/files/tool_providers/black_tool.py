from __future__ import annotations
import subprocess
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema
from app.enums.logging_enums import RunContext
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

class BlackToolProviderV2(ToolProviderBase):
    """
    Runs `black` either in --check (diff-only) mode or full formatting mode and
    maps Black’s native exit codes onto the 1 / 0 contract.
    """

    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        target_name: str = input.get("target")
        check: bool = bool(input.get("check", False))

        # Resolve and verify via FileManager
        resolved_type = fm.resolve_existing_filetype(target_name)
        if not fm.exists(resolved_type, target_name):
            raise FileNotFoundError(f"{target_name} not found")

        # Load content from storage
        content = fm.load(resolved_type, target_name)

        # Stage it in a temp file
        suffix    = Path(target_name).suffix or ".py"
        temp_path = fm.write_temp(content, suffix=suffix)

        # Update context lineage
        if context:
            context.parent_id = self._run_id
            context.execution_chain = context.execution_chain[:] + [self._run_id]

        # Build and run Black command against the temp file
        cmd = [
            sys.executable,
            "-m",
            "black",
            "--diff" if check else "--quiet",
            "--check" if check else "",
            str(temp_path),
        ]
        cmd = [c for c in cmd if c]

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
        except Exception as exc:
            return self._runtime_error(str(exc))

        raw_code = proc.returncode
        stdout   = (proc.stdout or "").strip()
        stderr   = (proc.stderr or "").strip()

        # Handle --check mode
        if check:
            if raw_code == 0:
                return self._success(
                    summary="✅ Black check passed (no reformatting needed)",
                    metrics={
                        "files_checked": 1,
                        "files_reformatted": 0,
                        "lines_changed": 0,
                        "raw_return_code": raw_code,
                    },
                )

            if raw_code == 1:
                diff_hunks = len(re.findall(r"^@@", stdout, re.MULTILINE))
                return self._failure(
                    stdout=stdout,
                    summary=(
                        f"❌ Black would reformat the file "
                        f"({diff_hunks} changed hunk{'s' if diff_hunks != 1 else ''})"
                    ),
                    violations=[f"WOULD_REFORMAT:{target_name}"],
                    metrics={
                        "files_checked": 1,
                        "files_reformatted": 1,
                        "lines_changed": diff_hunks,
                        "raw_return_code": raw_code,
                    },
                )

            return self._runtime_error(stderr or stdout, raw_code)

        # Handle full‐format mode
        if raw_code == 0:
            return self._success(
                summary="✅ Black formatted the file successfully",
                metrics={
                    "files_reformatted": 1,
                    "raw_return_code": raw_code,
                },
            )

        return self._runtime_error(stderr or stdout, raw_code)

    # ──────────────────────────────────────────────── helpers
    def _success(
        self,
        summary: str,
        stdout: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
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
        stdout: Optional[str],
        summary: str,
        violations: List[str],
        metrics: Dict[str, Any],
    ) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=0,
            stdout=stdout,
            stderr=None,
            violations=violations,
            metrics=metrics,
            summary=summary,
        )

    def _runtime_error(
        self,
        message: str,
        raw_code: int | None = None,
    ) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=0,
            stdout=None,
            stderr=message,
            violations=["RUNTIME_ERROR"],
            metrics={"raw_return_code": raw_code, "exception": 1},
            summary=f"❌ Black execution failed: {message}",
        )
