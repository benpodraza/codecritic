from __future__ import annotations

import ast
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from app.enums.logging_enums import RunContext
from app.providers.tool_provider_base import ToolProviderBase
from app.db.schemas import ToolOutputSchema
from app.utilities.file_management.file_utils import get_file_manager, FileManagerBase

fm = get_file_manager()


class SymbolGraphToolProvider(ToolProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        # ─── Fork context ────────────────────────────────────────────────────
        if context:
            context = deepcopy(context)
            context.parent_id = self._run_id
            context.execution_chain = context.execution_chain[:] + [str(self._run_id)]

        target  = input.get("target")
        recurse = bool(input.get("recurse", False))

        # ─── Build graph ────────────────────────────────────────────────────
        symbol_graph = SymbolGraph(file_manager=fm)
        symbol_graph.parse(target, recurse=recurse)

        result_json = json.dumps(symbol_graph.graph, indent=2)

        return ToolOutputSchema(
            return_code=1,
            stdout=result_json,
            stderr=None,
            violations=None,
            metrics=symbol_graph.graph,
            summary=f"Parsed symbol graph from {target}",
        )


class SymbolGraph:
    def __init__(self, file_manager: FileManagerBase):
        self.graph: Dict[str, Any] = {}
        self.fm = file_manager

    def parse(self, path: str, recurse: bool = False) -> None:
        # Determine where this lives in your storage
        ftype = self.fm.resolve_existing_filetype(path)

        # Use file-manager is_file/is_dir instead of Path.* directly
        if self.fm.is_file(path):
            files = [path]
        elif self.fm.is_dir(path):
            files = self.fm.list_files(ftype, recursive=recurse)
        else:
            raise FileNotFoundError(f"❌ Path not found or invalid: {path}")

        # Parse each file by name
        for fname in files:
            content = self.fm.load(ftype, fname)
            self._parse_file(fname, content)

    def _parse_file(self, filename: str, content: str) -> None:
        module = self._module_name(filename)
        tree   = ast.parse(content, filename=filename)
        visitor = _SymbolGraphVisitor(module, filename, self.graph)
        visitor.visit(tree)

    def _module_name(self, filename: str) -> str:
        # purely string-based, no FS calls
        return Path(filename).stem


class _SymbolGraphVisitor(ast.NodeVisitor):
    def __init__(self, module: str, file_path: str, graph: Dict[str, Any]) -> None:
        self.module    = module
        self.file_path = file_path
        self.graph     = graph
        self.scope: list[str] = []
        self.current: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)
        self.scope.pop()
        self.current = None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)
        self.scope.pop()
        self.current = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qual = self._qualify(node.name)
        self._record(qual, "class", node)
        self.scope.append(node.name)
        self.current = qual
        self.generic_visit(node)
        self.scope.pop()
        self.current = None

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
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
