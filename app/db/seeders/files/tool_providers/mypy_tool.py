import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class MypyToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")

        # Use strictest mypy options available inline
        cmd = [
            sys.executable, "-m", "mypy", target,
            "--strict",
            "--disallow-untyped-defs",
            "--disallow-incomplete-defs",
            "--disallow-untyped-calls",
            "--disallow-untyped-decorators",
            "--disallow-any-generics",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--no-implicit-optional",
            "--strict-equality"
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)

        raw_code = proc.returncode
        raw_stdout = proc.stdout.strip()
        raw_stderr = proc.stderr.strip()

        violations: list[str] = []
        metrics: dict[str, int] = {}

        if raw_code == 0:
            norm_code = 1
            summary = "Mypy strict check passed"
            metrics = {"error_count": 0}
        elif raw_code == 1:
            norm_code = 0
            summary = "Mypy strict violations detected"
            violations = [line.strip() for line in raw_stdout.splitlines() if line.strip()]
            metrics = {"error_count": len(violations)}
        else:
            raise RuntimeError(f"Mypy execution error ({raw_code}): {raw_stderr or raw_stdout}")

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=raw_stdout or None,
            stderr=raw_stderr or None,
            violations=violations or None,
            metrics=metrics or None,
            summary=summary
        )
