from __future__ import annotations

import subprocess
import sys

from ...abstract_classes.tool_provider_base import ToolProviderBase


class BlackToolProvider(ToolProviderBase):
    """Run the black formatter."""

    def _run(self, target: str, check: bool = False):
        cmd = [sys.executable, "-m", "black", target]
        if check:
            cmd.append("--check")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("black not installed") from exc
        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError("black failed")
        return proc
