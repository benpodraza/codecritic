# app/systems/symbol_graph/symbol_service.py

from pathlib import Path
from typing import Optional, List

from app.utils.symbol_graph.symbol_graph import SymbolGraphBuilder
from app.utils.symbol_graph.symbol_index import SymbolIndex
from app.utils.symbol_graph.symbol_info import SymbolInfo


class SymbolService:
    """
    Provides lookup and navigation access to the Symbol Graph.
    Used by context providers, analyzers, and agents for symbol discovery.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.index = SymbolIndex()
        self._build_index()

    def _build_index(self):
        builder = SymbolGraphBuilder(self.root_path)
        symbols = builder.build()
        self.index.bulk_add(symbols)

    def lookup(self, symbol: str, file_hint: Optional[str] = None) -> Optional[SymbolInfo]:
        return self.index.resolve_best_match(symbol, file_hint)

    def get_all(self) -> List[SymbolInfo]:
        return list(self.index.by_full_name.values())

    def get_symbols_in_file(self, file_path: str) -> List[SymbolInfo]:
        return [s for s in self.index.by_full_name.values() if s.file_path == file_path]

    def find_by_type(self, symbol_type: str) -> List[SymbolInfo]:
        return [s for s in self.index.by_full_name.values() if s.type == symbol_type]
