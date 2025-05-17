# app/systems/symbol_graph/symbol_index.py

from typing import Dict, Optional
from app.utils.symbol_graph.symbol_info import SymbolInfo


class SymbolIndex:
    """
    Maintains a searchable in-memory cache of symbols.
    Supports resolution by name or full path.
    """

    def __init__(self):
        self.by_full_name: Dict[str, SymbolInfo] = {}
        self.by_short_name: Dict[str, list[SymbolInfo]] = {}

    def add(self, symbol: SymbolInfo):
        self.by_full_name[symbol.full_name] = symbol
        self.by_short_name.setdefault(symbol.name, []).append(symbol)

    def bulk_add(self, symbols: list[SymbolInfo]):
        for s in symbols:
            self.add(s)

    def get_by_full_name(self, full_name: str) -> Optional[SymbolInfo]:
        return self.by_full_name.get(full_name)

    def get_by_name(self, name: str) -> list[SymbolInfo]:
        return self.by_short_name.get(name, [])

    def resolve_best_match(self, name: str, file_hint: Optional[str] = None) -> Optional[SymbolInfo]:
        candidates = self.get_by_name(name)
        if not candidates:
            return None
        if file_hint:
            for c in candidates:
                if file_hint in c.file_path:
                    return c
        return candidates[0]  # fallback
