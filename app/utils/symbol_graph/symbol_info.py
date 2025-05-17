# app/systems/symbol_graph/symbol_info.py

from dataclasses import dataclass
from typing import Optional, Literal

SymbolType = Literal["function", "class", "method"]


@dataclass
class SymbolInfo:
    """
    Represents a single symbol (function, class, or method) extracted from a codebase.
    Used by the SymbolGraph to track locations, parents, and routing.
    """
    name: str                        # Short symbol name (e.g., 'train_epoch')
    full_name: str                   # Fully qualified (e.g., 'ModelTrainer.train_epoch')
    type: SymbolType                # 'function', 'method', or 'class'
    file_path: str                   # Absolute or project-relative file path
    start_line: int
    end_line: int
    parent: Optional[str] = None     # Class or function enclosing it (if any)
    decorators: Optional[list[str]] = None
    docstring: Optional[str] = None
