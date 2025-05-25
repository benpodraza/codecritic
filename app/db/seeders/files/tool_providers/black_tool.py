from __future__ import annotations
import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase

class BlackToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> str:
        target = input.get("target")
        check = input.get("check", False)

        cmd = [sys.executable, "-m", "black", "--quiet", target]
        if check:
            cmd.append("--check")

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        self._log.debug(proc.stdout)
        if proc.stderr:
            self._log.error(proc.stderr)

        result = {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "return_code": proc.returncode
        }

        if proc.returncode != 0:
            raise RuntimeError(f"black failed: {proc.stderr}")

        return json.dumps(result)
