#!/usr/bin/env python
"""Minimal cyclomatic complexity runner used for testing."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def complexity_score(code: str) -> int:
    tree = ast.parse(code)
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.Try,
                ast.With,
                ast.And,
                ast.Or,
                ast.ExceptHandler,
            ),
        ):
            complexity += 1
    return complexity


def analyze_file(path: Path) -> str:
    code = path.read_text()
    score = complexity_score(code)
    return f"{path} - Complexity: {score}"


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    for arg in argv:
        p = Path(arg)
        if p.is_dir():
            for file in p.rglob("*.py"):
                print(analyze_file(file))
        elif p.is_file():
            print(analyze_file(p))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
