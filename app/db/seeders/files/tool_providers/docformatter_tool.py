import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase

class DocFormatterToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> str:
        target = input.get("target")
        check = input.get("check", False)

        cmd = [sys.executable, "-m", "docformatter", target, "--in-place"]
        if check:
            cmd.append("--check")

        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.stdout:
            self._log.debug(proc.stdout)
        if proc.stderr:
            self._log.error(proc.stderr)

        result = {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "return_code": proc.returncode
        }

        if proc.returncode != 0:
            raise RuntimeError(f"docformatter failed: {proc.stderr}")

        return json.dumps(result)
