import subprocess
import sys
import re

from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema


class BlackToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        check = input.get("check", False)

        # Build the Black command
        if check:
            cmd = [
                sys.executable,
                "-m",
                "black",
                "--diff",
                "--check",
                "--verbose",
                target,
            ]
        else:
            cmd = [sys.executable, "-m", "black", "--quiet", target]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        raw_stdout = proc.stdout or ""
        raw_stderr = proc.stderr or ""
        stdout = raw_stdout.rstrip()
        stderr = raw_stderr.rstrip()
        violations: list[str] = []
        metrics: dict[str, int | None] = {}

        if check:
            # Black’s exit codes in check mode:
            #   0 = clean (nothing to reformat)
            #   1 = “would reformat” (violations present)
            #  ≥2 = unexpected internal error
            if proc.returncode == 0:
                # PASS (no formatting needed)
                return_code = 1
                summary = "Black check passed (no formatting needed)"
                metrics = {
                    "files_checked": 1,
                    "files_reformatted": 0,
                    "lines_changed": 0,
                }
            elif proc.returncode == 1:
                # FAIL (formatting *would* change the file)
                return_code = 0
                summary = "Black check failed"
                # Count diff hunks to estimate how many lines would change:
                diff_hunks = len(re.findall(r"^@@", stdout, re.MULTILINE))
                metrics = {
                    "files_checked": 1,
                    "files_reformatted": 1,   # Black signals at least one reformat
                    "lines_changed": diff_hunks,
                }
                # Return a *list of strings*, not dicts:
                violations = [
                    f"Would reformat {target}"
                ]
            else:
                # Any exit code ≥2 indicates an unexpected failure
                raise RuntimeError(
                    f"Black execution error ({proc.returncode}): {stderr or stdout}"
                )
        else:
            # “apply formatting” mode: nonzero means failure
            if proc.returncode != 0:
                raise RuntimeError(f"Black formatting error: {stderr or stdout}")
            return_code = 1
            summary = "Black formatting applied"
            metrics = {
                "files_checked": 1,
                "files_reformatted": 1,
                "lines_changed": None,  # You could diff a temp copy to compute exact changes
            }

        # Now that violations is a list[str], Pydantic will accept it:
        return ToolOutputSchema(
            return_code=return_code,
            stdout=stdout or None,
            stderr=stderr or None,
            violations=violations or None,
            metrics=metrics or None,
            summary=summary,
        )
