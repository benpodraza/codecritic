import subprocess
import sys
import re
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class BlackToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        check = input.get("check", False)

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
            if proc.returncode == 0:
                return_code = 1
                lines_changed = 0
                files_reformatted = 0
                summary = f"✅ Black passed: {files_reformatted} reformats"
            elif proc.returncode == 1:
                return_code = 0
                diff_hunks = len(re.findall(r"^@@", stdout, re.MULTILINE))
                lines_changed = diff_hunks
                files_reformatted = 1
                summary = f"❌ Black failed: {files_reformatted} file, {lines_changed} lines reformatted"
                violations = [f"Would reformat {target}"]
            else:
                raise RuntimeError(
                    f"Black execution error ({proc.returncode}): {stderr or stdout}"
                )
        else:
            if proc.returncode != 0:
                raise RuntimeError(f"Black formatting error: {stderr or stdout}")
            return_code = 1
            lines_changed = None
            files_reformatted = 1
            summary = f"✅ Black formatted {files_reformatted} file"

        metrics = {
            "files_checked": 1,
            "files_reformatted": files_reformatted,
            "lines_changed": lines_changed,
            "raw_return_code": proc.returncode
        }

        return ToolOutputSchema(
            return_code=return_code,
            stdout=stdout or None,
            stderr=stderr or None,
            violations=violations or None,
            metrics=metrics or None,
            summary=summary,
        )
