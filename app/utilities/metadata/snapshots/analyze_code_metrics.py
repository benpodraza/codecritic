from __future__ import annotations

import ast
import tokenize
from io import StringIO
from typing import Any, Dict


def analyze_code(source: str) -> Dict[str, Any]:
    """Analyze Python source code and return structural metrics."""
    metrics: Dict[str, Any] = {}

    # === Basic line count ===
    lines = source.strip().splitlines()
    metrics["line_count"] = len(lines)

    # === AST-based metrics ===
    tree = ast.parse(source)
    symbols = set()

    metrics.update({
        "function_count": 0,
        "class_count": 0,
        "branch_count": 0,
        "call_count": 0,
        "assignment_count": 0,
        "return_count": 0,
        "exception_count": 0,
        "docstring_count": 0,
    })

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            metrics["function_count"] += 1
            symbols.add(node.name)
            if ast.get_docstring(node):
                metrics["docstring_count"] += 1
        elif isinstance(node, ast.ClassDef):
            metrics["class_count"] += 1
            symbols.add(node.name)
            if ast.get_docstring(node):
                metrics["docstring_count"] += 1
        elif isinstance(node, (ast.If, ast.For, ast.While, ast.Match, ast.With, ast.Try)):
            metrics["branch_count"] += 1
        elif isinstance(node, ast.Call):
            metrics["call_count"] += 1
        elif isinstance(node, ast.Assign):
            metrics["assignment_count"] += 1
        elif isinstance(node, ast.Return):
            metrics["return_count"] += 1
        elif isinstance(node, (ast.Try, ast.ExceptHandler, ast.Raise)):
            metrics["exception_count"] += 1

    metrics["symbol_count"] = len(symbols)

    # === Token-based metrics ===
    comment_count = 0
    import_count = 0
    try:
        tokens = tokenize.generate_tokens(StringIO(source).readline)
        for toknum, tokval, *_ in tokens:
            if toknum == tokenize.COMMENT:
                comment_count += 1
            elif toknum == tokenize.NAME and tokval in {"import", "from"}:
                import_count += 1
    except tokenize.TokenError:
        pass

    metrics["comment_count"] = comment_count
    metrics["import_count"] = import_count

    return metrics


def compute_deltas(before_metrics: dict, after_metrics: dict) -> dict:
    """Compute deltas between before/after metric sets."""
    return {
        f"{key}_delta": after_metrics.get(key, 0) - before_metrics.get(key, 0)
        for key in after_metrics
        if key in before_metrics
    }
