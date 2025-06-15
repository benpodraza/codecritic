import subprocess
import sys
from copy import deepcopy

from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema
from app.enums.logging_enums import RunContext


class DocFormatterToolProvider(ToolProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        target = input.get("target")
        check = input.get("check", False)

        # ✅ Propagate context
        if context:
            context = deepcopy(context)
            context.parent_id = self._run_id
            context.execution_chain = context.execution_chain[:] + [self._run_id]

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
                summary = "✅ Docstring format check passed"
            elif raw_code == 1:
                norm_code = 0
                summary = "❌ Docstring format check failed"
            else:
                return self._runtime_error(f"Docformatter check error ({raw_code}): {stderr or stdout}")
        else:
            if raw_code == 0:
                norm_code = 1
                summary = "✅ Docstrings formatted successfully"
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
