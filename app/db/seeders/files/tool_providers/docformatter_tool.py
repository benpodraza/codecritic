import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema
from app.enums.logging_enums import RunContext
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()

class DocFormatterToolProvider(ToolProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        # 1) Resolve and verify via FileManager
        target_name = input.get("target")
        resolved_type = fm.resolve_existing_filetype(target_name)
        if not fm.exists(resolved_type, target_name):
            raise FileNotFoundError(f"{target_name} not found")

        # 2) Load content from storage
        content = fm.load(resolved_type, target_name)

        # 3) Stage it in a temp file
        suffix    = Path(target_name).suffix or ".py"
        temp_path = fm.write_temp(content, suffix=suffix)

        # 4) Fork context if provided
        if context:
            context = deepcopy(context)
            context.parent_id       = self._run_id
            context.execution_chain = context.execution_chain[:] + [self._run_id]

        # 5) Build and run docformatter command
        cmd = [
            sys.executable,
            "-m",
            "docformatter",
            str(temp_path),
            "--in-place"
        ]
        if input.get("check", False):
            cmd.append("--check")

        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout   = proc.stdout.strip()
        stderr   = proc.stderr.strip()
        raw_code = proc.returncode

        # 6) Interpret results
        check = bool(input.get("check", False))
        if check:
            if raw_code == 0:
                norm_code = 1
                summary   = "✅ Docstring format check passed"
            elif raw_code == 1:
                norm_code = 0
                summary   = "❌ Docstring format check failed"
            else:
                return self._runtime_error(f"Docformatter check error ({raw_code}): {stderr or stdout}")
        else:
            if raw_code == 0:
                norm_code = 1
                summary   = "✅ Docstrings formatted successfully"
            else:
                return self._runtime_error(f"Docformatter formatting error ({raw_code}): {stderr or stdout}")

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=stdout,
            stderr=stderr,
            summary=summary
        )

    def _runtime_error(self, message: str) -> ToolOutputSchema:
        return ToolOutputSchema(
            return_code=0,
            stdout=None,
            stderr=message,
            violations=["RUNTIME_ERROR"],
            metrics={"exception": 1},
            summary=f"❌ docformatter execution failed: {message}",
        )
