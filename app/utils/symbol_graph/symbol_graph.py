# app/systems/symbol_graph/symbol_graph.py

import ast
from pathlib import Path
from typing import List

from app.utils.symbol_graph.symbol_info import SymbolInfo


class SymbolGraphBuilder:
    """
    Builds a graph of all top-level and nested symbols in a Python file or directory.
    Extracts classes, functions, and methods with line ranges and metadata.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.symbols: List[SymbolInfo] = []

    def build(self) -> List[SymbolInfo]:
        py_files = self._gather_py_files()
        for file in py_files:
            self._extract_symbols_from_file(file)
        return self.symbols

    def _gather_py_files(self) -> List[Path]:
        if self.root_path.is_file():
            return [self.root_path]
        return list(self.root_path.rglob("*.py"))

    def _extract_symbols_from_file(self, file_path: Path):
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            visitor = _SymbolExtractorVisitor(str(file_path))
            visitor.visit(tree)
            self.symbols.extend(visitor.symbols)
        except Exception as e:
            print(f"⚠️ Failed to parse {file_path}: {e}")


class _SymbolExtractorVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.symbols: List[SymbolInfo] = []
        self.file_path = file_path
        self.stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        fqname = ".".join(self.stack + [node.name])
        self.symbols.append(SymbolInfo(
            name=node.name,
            full_name=fqname,
            type="class",
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            parent=self.stack[-1] if self.stack else None,
            decorators=[d.id for d in node.decorator_list if isinstance(d, ast.Name)],
            docstring=ast.get_docstring(node)
        ))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        fqname = ".".join(self.stack + [node.name])
        symbol_type = "method" if self.stack else "function"
        self.symbols.append(SymbolInfo(
            name=node.name,
            full_name=fqname,
            type=symbol_type,
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno),
            parent=self.stack[-1] if self.stack else None,
            decorators=[d.id for d in node.decorator_list if isinstance(d, ast.Name)],
            docstring=ast.get_docstring(node)
        ))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()
