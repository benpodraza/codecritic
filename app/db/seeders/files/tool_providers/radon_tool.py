import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from app.enums.logging_enums import RunContext
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

class RadonToolProvider(ToolProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        # 1) Resolve and verify via FileManager
        target_name   = input.get("target")
        resolved_type = fm.resolve_existing_filetype(target_name)
        if not fm.exists(resolved_type, target_name):
            raise FileNotFoundError(f"{target_name} not found")

        # 2) Load the content from your storage layer
        content = fm.load(resolved_type, target_name)

        # 3) Stage it in a temp file (still via FileManager)
        suffix    = Path(target_name).suffix or ".py"
        temp_path = fm.write_temp(content, suffix=suffix)

        # 4) Fork context if needed
        if context:
            context       = deepcopy(context)
            context.parent_id        = self._run_id
            context.execution_chain  = context.execution_chain[:] + [self._run_id]

        # 5) Run Radon on the temp file
        cmd  = [sys.executable, "-m", "radon", "cc", "-s", str(temp_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        stdout   = proc.stdout.strip()
        stderr   = proc.stderr.strip()
        raw_code = proc.returncode

        if raw_code != 0:
            raise RuntimeError(f"radon failed: {stderr or stdout or 'unknown error'}")

        # 6) Parse grades
        grades = []
        for line in stdout.splitlines():
            if "(" in line and ")" in line:
                try:
                    grades.append(line.split("(", 1)[1].split(")")[0])
                except Exception:
                    continue

        worst_grade = max(grades, default="A")
        passing     = worst_grade in ("A", "B")

        norm_code = 1 if passing else 0
        summary   = (
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
