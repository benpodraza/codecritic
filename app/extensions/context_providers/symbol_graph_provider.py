from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Set

from ...abstract_classes.context_provider_base import ContextProviderBase


class SymbolGraphProvider(ContextProviderBase):
    """Generate a simple symbol graph for a Python module."""

    def __init__(self, module_path: str) -> None:
        super().__init__()
        self.module_path = Path(module_path)

    def _get_context(self) -> Dict[str, Any]:
        """Parse the module and return context information."""
        if not self.module_path.exists():
            self.logger.error("Module not found: %s", self.module_path)
            return {}

        source = self.module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        functions: List[str] = []
        classes: Dict[str, List[str]] = {}
        call_map: Dict[str, Set[str]] = {}

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                sig = self._format_signature(node)
                functions.append(sig)
                call_map[node.name] = self._collect_calls(node)
            elif isinstance(node, ast.ClassDef):
                method_sigs: List[str] = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        sig = self._format_signature(item)
                        method_sigs.append(sig)
                        key = f"{node.name}.{item.name}"
                        call_map[key] = self._collect_calls(item)
                classes[node.name] = method_sigs

        context = {
            "functions": functions,
            "classes": classes,
            "call_map": {k: sorted(v) for k, v in call_map.items()},
        }
        self.logger.info("Context generated for %s", self.module_path)
        return context

    def _format_signature(self, func: ast.FunctionDef) -> str:
        args = [arg.arg for arg in func.args.args]
        if func.args.vararg:
            args.append("*" + func.args.vararg.arg)
        for kw in func.args.kwonlyargs:
            args.append(kw.arg)
        if func.args.kwarg:
            args.append("**" + func.args.kwarg.arg)
        return f"{func.name}({', '.join(args)})"

    def _collect_calls(self, func: ast.FunctionDef) -> Set[str]:
        calls: Set[str] = set()
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
        return calls
