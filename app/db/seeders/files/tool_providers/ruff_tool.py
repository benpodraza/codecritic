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

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        raw_code = proc.returncode

        violations = []

        if raw_code in (0, 1):  # 1 = violations, 0 = clean
            for line in stdout.splitlines():
                if line.strip().startswith(target):
                    parts = line.strip().split()
                    if parts:
                        violations.append(parts[-1])  # Capture violation code

        if raw_code == 0:
            norm_code = 1  # ✅ pass
            summary = "Ruff check passed"
        elif raw_code == 1:
            norm_code = 0  # ❌ fail
            summary = "Ruff rule violations found"
        else:
            raise RuntimeError(f"Ruff execution error ({raw_code}): {stderr or stdout or 'unknown error'}")

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=stdout,
            stderr=stderr,
            violations=violations or None,
            summary=summary
        )
