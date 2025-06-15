import subprocess
import sys
from pathlib import Path
from copy import deepcopy

from app.enums.logging_enums import RunContext
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema


class RadonToolProvider(ToolProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        target = input.get("target")
        if not Path(target).exists():
            raise FileNotFoundError(f"{target} not found")

        # ✅ Clone context and inject ancestry
        if context:
            context = deepcopy(context)
            context.parent_id = self._run_id
            context.execution_chain = context.execution_chain[:] + [self._run_id]

        cmd = [sys.executable, "-m", "radon", "cc", "-s", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        raw_code = proc.returncode

        if raw_code != 0:
            raise RuntimeError(f"radon failed: {stderr or stdout or 'unknown error'}")

        # Determine worst grade
        grades = []
        for line in stdout.splitlines():
            if line.strip() and "(" in line and ")" in line:
                try:
                    grade = line.strip().split("(", 1)[1].split(")")[0]
                    grades.append(grade)
                except Exception:
                    continue

        worst_grade = max(grades, default="A")
        passing = worst_grade in ("A", "B")

        norm_code = 1 if passing else 0
        summary = (
            f"Radon complexity OK (worst: {worst_grade})"
            if passing else
            f"Radon complexity too high (worst: {worst_grade})"
        )

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=stdout,
            stderr=stderr,
            summary=summary,
        )
