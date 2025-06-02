import subprocess
import sys
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class DocFormatterToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        check = input.get("check", False)

        cmd = [sys.executable, "-m", "docformatter", target, "--in-place"]
        if check:
            cmd.append("--check")

        proc = subprocess.run(cmd, capture_output=True, text=True)

        summary = (
            "Docstrings formatted" if not check and proc.returncode == 0 else
            "Docstring format check passed" if check and proc.returncode == 0 else
            "Docstring format check failed"
        )

        if proc.returncode != 0 and not check:
            raise RuntimeError(f"docformatter failed: {proc.stderr}")

        return ToolOutputSchema(
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            summary=summary
        )
