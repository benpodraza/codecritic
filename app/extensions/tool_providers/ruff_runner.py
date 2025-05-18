from __future__ import annotations

import subprocess
import sys

from ...abstract_classes.tool_provider_base import ToolProviderBase


class RuffToolProvider(ToolProviderBase):
    def _run(self, target: str):
        cmd = [sys.executable, "-m", "ruff", "check", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.stdout:
            self._log.debug(proc.stdout)
        if proc.stderr:
            self._log.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError(f"ruff failed: {proc.stderr}")
        return proc
