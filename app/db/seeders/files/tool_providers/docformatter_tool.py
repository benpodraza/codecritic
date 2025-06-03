import subprocess
import sys
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class DocFormatterToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        check = input.get("check", False)

        # Build command
        cmd = [sys.executable, "-m", "docformatter", target, "--in-place"]
        if check:
            cmd.append("--check")

        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        raw_code = proc.returncode

        if check:
            if raw_code == 0:
                norm_code = 1
                summary = "Docstring format check passed"
            elif raw_code == 1:
                norm_code = 0
                summary = "Docstring format check failed"
            else:
                raise RuntimeError(f"docformatter check error ({raw_code}): {stderr or stdout}")
        else:
            if raw_code == 0:
                norm_code = 1
                summary = "Docstrings formatted successfully"
            else:
                raise RuntimeError(f"docformatter formatting error ({raw_code}): {stderr or stdout}")

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=stdout,
            stderr=stderr,
            summary=summary
        )
