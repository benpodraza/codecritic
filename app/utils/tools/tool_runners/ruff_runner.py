"""
ruff_runner: Lints and optionally fixes Python code using Ruff.
"""
import subprocess

def run_ruff(code: str) -> str:
    try:
        proc = subprocess.run(
            ["ruff", "--fix", "-"],
            input=code.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return proc.stdout.decode("utf-8") or code
    except Exception:
        return code