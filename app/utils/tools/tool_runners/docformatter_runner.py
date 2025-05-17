"""
docformatter_runner: Formats docstrings using docformatter.
"""
import subprocess

def run_docformatter(code: str) -> str:
    try:
        proc = subprocess.run(
            ["docformatter", "--stdin", "--wrap-summaries", "88", "--wrap-descriptions", "88"],
            input=code.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        return proc.stdout.decode("utf-8") or code
    except Exception:
        return code