from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict

from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema


class SymbolGraph:
    def __init__(self) -> None:
        self.graph = {}

    def parse_file(self, filepath: str | Path) -> None:
        from ast import parse
        filepath = Path(filepath)
        source = filepath.read_text(encoding="utf-8")
        tree = parse(source, filename=str(filepath))

        visitor = _SymbolGraphVisitor(filepath.stem, str(filepath), self.graph)
        visitor.visit(tree)


class SymbolGraphToolProvider(ToolProviderBase):
    def _run(self, input: dict) -> ToolOutputSchema:
        target = input.get("target")
        path = Path(target)
        if not path.exists():
            raise FileNotFoundError(f"{target} does not exist")

        symbol_graph_util = SymbolGraph()
        symbol_graph_util.parse_file(target)

        result_json = json.dumps(symbol_graph_util.graph, indent=2)
        return ToolOutputSchema(
            return_code=0,
            stdout=result_json,
            metrics=symbol_graph_util.graph,
            summary="Symbol graph extraction successful"
        )


class _SymbolGraphVisitor(ast.NodeVisitor):
    def __init__(self, module: str, file_path: str, graph: Dict[str, Any]) -> None:
        self.module = module
        self.file_path = file_path
        self.graph = graph
        self.scope = []
        self.current = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function_or_async_function(node)
        self.generic_visit(node)
        self.scope.pop()
        self.current = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function_or_async_function(node)
        self.generic_visit(node)
        self.scope.pop()
        self.current = None

    def _process_function_or_async_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        qual = self._qualify(node.name)
        self.graph[qual] = {
            "name": node.name,
            "type": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
            "file": self.file_path,
            "lineno": node.lineno,
            "col_offset": node.col_offset,
            "end_lineno": getattr(node, "end_lineno", node.lineno),
            "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            "scope": ".".join([self.module, *self.scope]) if self.scope else self.module,
            "calls": [],
        }
        self.scope.append(node.name)
        self.current = qual

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qual = self._qualify(node.name)
        self._record(qual, "class", node)
        self.scope.append(node.name)
        self.current = qual
        self.generic_visit(node)
        self.scope.pop()
        self.current = None

    def _qualify(self, name: str) -> str:
        return ".".join([self.module, *self.scope, name])

    def _record(self, qual: str, typ: str, node: ast.AST) -> Dict[str, Any]:
        info = {
            "type": typ,
            "file": self.file_path,
            "lineno": getattr(node, "lineno", None),
            "col_offset": getattr(node, "col_offset", None),
            "end_lineno": getattr(node, "end_lineno", getattr(node, "lineno", None)),
            "end_col_offset": getattr(node, "end_col_offset", getattr(node, "col_offset", None)),
            "scope": ".".join([self.module, *self.scope]) if self.scope else self.module,
            "calls": [],
        }
        self.graph[qual] = info
        return info
