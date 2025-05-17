from __future__ import annotations
import subprocess
import sys
from ...abstract_classes.tool_provider_base import ToolProviderBase


class RadonToolProvider(ToolProviderBase):
    def _run(self, target: str):
        # Call radon via -m so it returns a CompletedProcess
        cmd = [sys.executable, "-m", "radon", "cc", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)

        if proc.returncode != 0:
            raise RuntimeError(f"radon failed: {proc.stderr.strip()}")

        return proc
