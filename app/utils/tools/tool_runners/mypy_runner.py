"""
mypy_runner: Runs MyPy type checks and returns output or diagnostics.
"""

import subprocess
import tempfile
import os

def run_mypy(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        proc = subprocess.run(
            ["mypy", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return proc.stdout.decode("utf-8").strip()

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
