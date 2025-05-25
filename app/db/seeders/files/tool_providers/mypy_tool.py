import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase

class MypyToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> str:
        target = input.get("target")

        cmd = [sys.executable, "-m", "mypy", target]
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

        if proc.returncode not in (0, 1):  # 1 means lint issues; not failure
            raise RuntimeError(f"mypy execution error: {proc.stderr}")

        return json.dumps(result)
