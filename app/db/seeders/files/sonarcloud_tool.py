from __future__ import annotations
import subprocess

from app.abstract_classes.tool_provider_base import ToolProviderBase


class SonarCloudToolProvider(ToolProviderBase):
    def _run(self, target: str):
        # Simple stub that doesn't use relative paths
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")

