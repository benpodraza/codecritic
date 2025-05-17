from __future__ import annotations

import subprocess
import sys

from ...abstract_classes.tool_provider_base import ToolProviderBase


class MypyToolProvider(ToolProviderBase):
    """Run the mypy static type checker."""

    def _run(self, target: str):
        cmd = [sys.executable, "-m", "mypy", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            fallback = ["mypy", target]
            proc = subprocess.run(fallback, capture_output=True, text=True)
        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError("mypy failed")
        return proc
