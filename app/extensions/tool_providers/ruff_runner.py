from __future__ import annotations

import subprocess
import sys

from ...abstract_classes.tool_provider_base import ToolProviderBase


class RuffToolProvider(ToolProviderBase):
    """Run the ruff linter."""

    def _run(self, target: str):
        cmd = [sys.executable, "-m", "ruff", "check", target]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("ruff not installed") from exc
        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError("ruff failed")
        return proc
