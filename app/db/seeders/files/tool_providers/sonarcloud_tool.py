from __future__ import annotations
import subprocess
from pathlib import Path
from app.providers.tool_provider_base import ToolProviderBase

class SonarCloudToolProvider(ToolProviderBase):
    def _run(self, target: str) -> subprocess.CompletedProcess:
        if not Path(target).exists():
            raise FileNotFoundError(f"{target} does not exist")

        return subprocess.CompletedProcess(
            args=["sonarcloud", target],
            returncode=0,
            stdout="{}",
            stderr="",
        )
