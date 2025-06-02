import subprocess
import sys
import json
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema

class BlackToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        check = input.get("check", False)

        cmd = [sys.executable, "-m", "black", "--quiet", target]
        if check:
            cmd.append("--check")

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        summary = (
            "Black check passed (code formatted correctly)"
            if proc.returncode == 0 and check else
            "Black formatting applied" if proc.returncode == 0 else
            "Black check failed"
        )

        if proc.returncode != 0 and not check:
            raise RuntimeError(f"black failed: {proc.stderr}")

        return ToolOutputSchema(
            return_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            summary=summary
        )
