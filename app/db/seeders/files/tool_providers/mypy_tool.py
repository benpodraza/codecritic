import subprocess
import sys
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class MypyToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")

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
            error_count = 0
        elif raw_code == 1:
            norm_code = 0
            violations = [line.strip() for line in raw_stdout.splitlines() if line.strip()]
            error_count = len(violations)
        else:
            raise RuntimeError(f"Mypy execution error ({raw_code}): {raw_stderr or raw_stdout}")

        summary = (
            f"✅ Mypy passed: {error_count} errors"
            if norm_code == 1
            else f"❌ Mypy failed: {error_count} errors"
        )

        metrics = {"error_count": error_count, "raw_return_code": raw_code}

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=raw_stdout or None,
            stderr=raw_stderr or None,
            violations=violations or None,
            metrics=metrics,
            summary=summary,
        )
