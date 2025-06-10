import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class RuffToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")

        # 1) Run Ruff in JSON mode
        cmd = [sys.executable, "-m", "ruff", "check", "--format", "json", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        raw_code = proc.returncode

        # 2) Try parsing JSON; if that fails, mark parse_error
        parse_error = False
        violations = []

        try:
            report = json.loads(stdout)
            for file_report in report:
                for v in file_report.get("violations", []):
                    violations.append(v["code"])
        except json.JSONDecodeError:
            parse_error = True

        # 3) Score parse errors as a heavy penalty (10 violations)
        if parse_error:
            violations = ["PARSE_ERROR"]
            violation_count = 1
        else:
            violation_count = len(violations)

        # 4) Build summary & normalized return code
        if parse_error:
            norm_code = 0
            summary = f"❌ Ruff parse error ({violation_count} violations)"
        elif raw_code == 0:
            norm_code = 1
            summary = f"✅ Ruff passed: {violation_count} violations"
        elif raw_code == 1:
            norm_code = 0
            summary = f"❌ Ruff failed: {violation_count} violations"
        else:
            norm_code = 2
            summary = f"❌ Ruff execution error ({raw_code})"

        metrics = {
            "violation_count": violation_count,
            "raw_return_code": raw_code,
            "parse_error": parse_error
        }

        return ToolOutputSchema(
            return_code=norm_code,
            stdout=stdout.strip() or None,
            stderr=stderr.strip() or None,
            violations=violations,
            metrics=metrics,
            summary=summary,
        )
