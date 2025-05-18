from __future__ import annotations

import subprocess
import sys

from ...abstract_classes.tool_provider_base import ToolProviderBase


class MypyToolProvider(ToolProviderBase):
    def _run(self, target: str):
        cmd = [sys.executable, "-m", "mypy", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.stdout:
            self._log.debug(proc.stdout)
        if proc.stderr:
            self._log.error(proc.stderr)
        if proc.returncode not in (0, 1):  # mypy returns 1 if it finds issues
            raise RuntimeError(f"mypy execution error: {proc.stderr}")
        return proc
