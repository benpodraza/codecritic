"""
black_runner: Formats Python code using Black.
"""

import subprocess


def run_black(code: str) -> str:
    try:
        proc = subprocess.run(
            ["black", "-", "--quiet"],
            input=code.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return proc.stdout.decode("utf-8") or code
    except Exception:
        return code 