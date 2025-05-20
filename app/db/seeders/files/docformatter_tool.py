import subprocess
import sys
from app.abstract_classes.tool_provider_base import ToolProviderBase


class DocFormatterToolProvider(ToolProviderBase):
    def _run(self, target: str, check: bool = False):
        cmd = [sys.executable, "-m", "docformatter", target, "--in-place"]
        if check:
            cmd.append("--check")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.stdout:
            self._log.debug(proc.stdout)
        if proc.stderr:
            self._log.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError(f"docformatter failed: {proc.stderr}")
        return proc
