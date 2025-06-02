import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class MypyToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")

        cmd = [sys.executable, "-m", "mypy", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        return_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr

        summary = (
            "Mypy check passed"
            if return_code == 0 else
            "Mypy type issues detected"
            if return_code == 1 else
            f"Mypy error ({return_code})"
        )

        if return_code not in (0, 1):  # 1 = valid analysis with issues
            raise RuntimeError(f"Mypy execution error: {stderr or stdout}")

        return ToolOutputSchema(
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            summary=summary
        )
