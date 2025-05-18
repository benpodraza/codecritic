from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List, MutableMapping

from ...abstract_classes.context_provider_base import ContextProviderBase
from ...factories.logging_provider import LoggingProvider
from ...utilities.snapshots.snapshot_writer import SnapshotWriter
from ...enums.agent_enums import AgentRole


class SymbolGraphProvider(ContextProviderBase):
    """Generate a detailed symbol graph for a Python module or package."""

    def __init__(
        self,
        target: str | None = None,
        module_path: str | None = None,
        logger: LoggingProvider | None = None,
        snapshot_writer: SnapshotWriter | None = None,
    ) -> None:
        super().__init__(logger)
        # allow both 'target' and legacy 'module_path'
        path_str = module_path if module_path is not None else target
        if path_str is None:
            raise ValueError("SymbolGraphProvider requires 'target' or 'module_path'")
        self.target = Path(path_str)
        self.snapshot_writer = snapshot_writer or SnapshotWriter()
        self._graph: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def resolve_symbol(self, name: str) -> Dict[str, Any] | None:
        """Return details for a fully qualified symbol."""
        return self._graph.get(name)

    # ------------------------------------------------------------------
    # ContextProviderBase implementation
    # ------------------------------------------------------------------
    def _get_context(self) -> Dict[str, Any]:
        if not self.target.exists():
            self._log.error("Target not found: %s", self.target)
            return {}

        self._graph.clear()

        paths = [self.target]
        if self.target.is_dir():
            paths = list(self.target.rglob("*.py"))

        for path in paths:
            self._parse_file(path)

        self._log.info("Symbol graph built for %s", self.target)

        try:
            self.snapshot_writer.write_snapshot(
                experiment_id="context",
                round=0,
                file_path=f"{self.target}.symbol_graph.json",
                before="",
                after=json.dumps(self._graph, indent=2),
                symbol=str(self.target),
                agent_role=AgentRole.GENERATOR,
            )
        except Exception:
            self._log.exception("Failed to snapshot symbol graph")

        return {"symbol_graph": self._graph}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _parse_file(self, path: Path) -> None:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        module_name = self._module_name(path)

        visitor = _SymbolGraphVisitor(module_name, str(path), self._graph)
        visitor.visit(tree)

    def _module_name(self, path: Path) -> str:
        if self.target.is_file():
            return path.stem
        rel = path.relative_to(self.target)
        return ".".join(rel.with_suffix("").parts)


class _SymbolGraphVisitor(ast.NodeVisitor):
    """AST visitor building a symbol graph."""

    def __init__(
        self, module: str, file_path: str, graph: MutableMapping[str, Dict[str, Any]]
    ) -> None:
        self.module = module
        self.file_path = file_path
        self.graph = graph
        self.scope: List[str] = []
        self.current: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Record function definition and track calls
        qual = self._qualify(node.name)
        info: Dict[str, Any] = {
            "name": node.name,
            "type": "function",
            "file": self.file_path,
            "lineno": node.lineno,
            "col_offset": node.col_offset,
            "end_lineno": getattr(node, "end_lineno", node.lineno),
            "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            "scope": (
                ".".join([self.module, *self.scope]) if self.scope else self.module
            ),
            "calls": [],
        }
        self.graph[qual] = info
        # Enter function scope
        self.scope.append(node.name)
        prev_current = self.current
        self.current = qual
        self.generic_visit(node)
        # Exit function scope
        self.scope.pop()
        self.current = prev_current

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        # Record async function definition and track calls
        qual = self._qualify(node.name)
        info: Dict[str, Any] = {
            "name": node.name,
            "type": "async_function",
            "file": self.file_path,
            "lineno": node.lineno,
            "col_offset": node.col_offset,
            "end_lineno": getattr(node, "end_lineno", node.lineno),
            "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            "scope": (
                ".".join([self.module, *self.scope]) if self.scope else self.module
            ),
            "calls": [],
        }
        self.graph[qual] = info
        # Enter async function scope
        self.scope.append(node.name)
        prev_current = self.current
        self.current = qual
        self.generic_visit(node)
        # Exit async function scope
        self.scope.pop()
        self.current = prev_current

    def _process_function_or_async_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        qual = self._qualify(node.name)
        info: Dict[str, Any] = {
            "name": node.name,
            "type": (
                "async_function"
                if isinstance(node, ast.AsyncFunctionDef)
                else "function"
            ),
            "file": self.file_path,
            "lineno": node.lineno,
            "col_offset": node.col_offset,
            "end_lineno": getattr(node, "end_lineno", node.lineno),
            "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            "scope": (
                ".".join([self.module, *self.scope]) if self.scope else self.module
            ),
            "calls": [],
        }
        self.graph[qual] = info
        self.scope.append(node.name)
        self.current = qual

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qual = self._qualify(node.name)
        self._record(qual, "class", node)
        self.scope.append(node.name)
        self.current = qual
        self.generic_visit(node)
        self.scope.pop()
        self.current = (
            ".".join([self.module, *self.scope]) if self.scope else self.module
        )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._record(self._qualify(target.id), "variable", target)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname or alias.name
            entry = self._record(self._qualify(name), "import", node)
            entry["target"] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            name = alias.asname or alias.name
            entry = self._record(self._qualify(name), "import", node)
            entry["target"] = (
                f"{node.module}.{alias.name}" if node.module else alias.name
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Determine current symbol context
        current = self.current or self.module
        # Identify called name
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called_name = node.func.attr
        else:
            called_name = None
        if called_name:
            self.graph.setdefault(current, {}).setdefault("calls", []).append(
                called_name
            )
        self.generic_visit(node)

    def _qualify(self, name: str) -> str:
        return ".".join([self.module, *self.scope, name])

    def _record(self, qual: str, typ: str, node: ast.AST) -> Dict[str, Any]:
        lineno = getattr(node, "lineno", None)
        col_offset = getattr(node, "col_offset", None)
        end_lineno = getattr(node, "end_lineno", lineno)
        end_col_offset = getattr(node, "end_col_offset", col_offset)
        info: Dict[str, Any] = {
            "type": typ,
            "file": self.file_path,
            "lineno": lineno,
            "col_offset": col_offset,
            "end_lineno": end_lineno,
            "end_col_offset": end_col_offset,
            "scope": (
                ".".join([self.module, *self.scope]) if self.scope else self.module
            ),
            "calls": [],
        }
        self.graph[qual] = info
        return info
