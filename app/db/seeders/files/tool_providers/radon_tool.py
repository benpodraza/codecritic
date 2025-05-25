import subprocess
import sys
import json
from pathlib import Path
from app.providers.tool_provider_base import ToolProviderBase

class RadonToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> str:
        target = input.get("target")
        if not Path(target).exists():
            raise FileNotFoundError(f"{target} not found")

        cmd = [sys.executable, "-m", "radon", "cc", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            raise RuntimeError(f"radon failed: {proc.stderr.strip()}")

        result = {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "return_code": proc.returncode
        }

        return json.dumps(result)
