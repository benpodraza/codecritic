import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase

class RuffToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> str:
        target = input.get("target")

        cmd = [sys.executable, "-m", "ruff", "check", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.stdout:
            self._log.debug(proc.stdout)
        if proc.stderr:
            self._log.error(proc.stderr)

        # Interpret output
        result = {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "return_code": proc.returncode,
        }

        # Only raise if ruff failed due to actual error (not rule violations)
        if proc.returncode > 1:
            self._log.error(f"❌ Ruff failed: {proc.stderr or proc.stdout or 'unknown error'}")
            raise RuntimeError(f"ruff execution error: {proc.stderr or proc.stdout or 'unknown error'}")

        # Log structured info for visibility
        self._log.debug(f"✅ Ruff completed with return code {proc.returncode}")
        self._log.debug(json.dumps(result, indent=2))

        return json.dumps(result)
