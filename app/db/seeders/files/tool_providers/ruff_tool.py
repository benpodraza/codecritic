import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class RuffToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")

        cmd = [sys.executable, "-m", "ruff", "check", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        stdout = proc.stdout
        stderr = proc.stderr
        return_code = proc.returncode

        # Default: no violations parsed
        violations = []
        if return_code in (0, 1):  # 1 = rule violations, not error
            for line in stdout.splitlines():
                if line.strip().startswith(target):
                    code = line.strip().split(" ")[-1]
                    violations.append(code)

        summary = (
            "Clean" if return_code == 0
            else "Lint rule violations found"
            if return_code == 1
            else f"Ruff execution error ({return_code})"
        )

        if return_code > 1:
            raise RuntimeError(f"Ruff failed: {stderr or stdout or 'unknown error'}")

        return ToolOutputSchema(
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            violations=violations,
            summary=summary
        )
