import subprocess
import sys
import json
from pathlib import Path
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class RadonToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        if not Path(target).exists():
            raise FileNotFoundError(f"{target} not found")

        cmd = [sys.executable, "-m", "radon", "cc", target]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        return_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr

        summary = (
            "Radon completed successfully" if return_code == 0
            else f"Radon failed with code {return_code}"
        )

        if return_code != 0:
            raise RuntimeError(f"radon failed: {stderr.strip() or stdout.strip()}")

        return ToolOutputSchema(
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            summary=summary
        )
