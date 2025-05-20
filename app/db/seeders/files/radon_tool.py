from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from app.abstract_classes.tool_provider_base import ToolProviderBase

class RadonToolProvider(ToolProviderBase):
    def _run(self, target: str) -> subprocess.CompletedProcess:
        if not Path(target).exists():
            raise FileNotFoundError(f"{target} not found")  # move up

        cmd = [sys.executable, "-m", "radon", "cc", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            raise RuntimeError(f"radon failed: {proc.stderr.strip()}")

        return proc

