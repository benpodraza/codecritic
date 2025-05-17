from __future__ import annotations
import subprocess
import sys
from ...abstract_classes.tool_provider_base import ToolProviderBase

class BlackToolProvider(ToolProviderBase):
    def _run(self, target: str, check: bool = False):
        # Use quiet mode to suppress emojis and extra output on Windows
        cmd = [sys.executable, "-m", "black", "--quiet", target]
        if check:
            cmd.append("--check")
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError(f"black failed: {proc.stderr}")
        return proc
