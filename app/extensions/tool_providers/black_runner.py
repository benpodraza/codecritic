from __future__ import annotations

import subprocess

from ...abstract_classes.tool_provider_base import ToolProviderBase


class BlackToolProvider(ToolProviderBase):
    """Run the black formatter."""

    def _run(self, target: str, check: bool = False):
        cmd = ["black", target]
        if check:
            cmd.append("--check")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError("black failed")
        return proc
