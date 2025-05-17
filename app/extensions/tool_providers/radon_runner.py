from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ...abstract_classes.tool_provider_base import ToolProviderBase


class RadonToolProvider(ToolProviderBase):
    """Run cyclomatic complexity analysis using the bundled runner."""

    def _run(self, target: str):
        script = Path(__file__).resolve().parents[3] / "tools" / "radon_runner.py"
        cmd = [sys.executable, str(script), target]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("radon runner not found") from exc
        if proc.stdout:
            self.logger.debug(proc.stdout)
        if proc.stderr:
            self.logger.error(proc.stderr)
        if proc.returncode != 0:
            raise RuntimeError("radon failed")
        return proc
