"""
ContextProviderPreprocessor: shared context logic for preprocessing systems.

Used as a base by Generator, Discriminator, and Mediator context injectors.
"""

from pathlib import Path
from typing import Any
import re
import json

from app.utils.agents.base_agent.context_provider import ContextProvider
from app.utils.symbol_graph.symbol_service import SymbolService

# === CONSTANTS ===
META_SUFFIX = "_children"


class ContextProviderPreprocessor(ContextProvider):
    def __init__(self, symbol_service: SymbolService):
        self.symbol_service = symbol_service

    def get_context(self, inputs: dict[str, Any]) -> dict:
        symbol = inputs.get("symbol")
        file_path = Path(inputs.get("file"))
        return self._build_context(symbol, file_path)

    def _build_context(self, symbol: str, file_path: Path) -> dict:
        root = file_path.parent
        children_dir = root / f"{file_path.stem}{META_SUFFIX}"

        # Retrieve symbol metadata
        symbol_info = self.symbol_service.lookup(symbol, str(file_path))

        context = {
            "symbol": symbol,
            "source_file": str(file_path),
            "children": [],
            "breadcrumbs": 0,
            "logger_calls": 0,
            "metadata": [],
            "resolved_imports": {},
            "symbol_info": symbol_info.__dict__ if symbol_info else {},
            "max_lines_per_function": 20,
            "variant": "zero_shot"
        }

        if children_dir.exists():
            for f in sorted(children_dir.glob("*.py")):
                code = f.read_text(encoding="utf-8")
                if symbol in code:
                    context["children"].append({
                        "file": str(f),
                        "content": code,
                        "metadata": self._extract_metadata_footer(f)
                    })
                    context["breadcrumbs"] += code.count("BREADCRUMB:")
                    context["logger_calls"] += code.count("logger.")

        context["resolved_imports"] = self._resolve_imports(file_path)
        return context



    def _extract_metadata_footer(self, path: Path) -> dict:
        text = path.read_text(encoding="utf-8")
        lines = text.strip().splitlines()
        footer_lines = [l for l in lines if l.startswith("# === AI-FIRST METADATA ===") or l.startswith("# ")]
        meta = {}
        for line in footer_lines:
            if line.startswith("# === AI-FIRST METADATA ==="):
                continue
            if line.startswith("# "):
                keyval = line[2:].split(":", 1)
                if len(keyval) == 2:
                    key, val = keyval
                    meta[key.strip()] = val.strip()
        return meta

    def _resolve_imports(self, file_path: Path) -> dict:
        text = file_path.read_text(encoding="utf-8")
        import_lines = [line for line in text.splitlines() if line.startswith("from ") or line.startswith("import ")]
        resolved = {}

        for line in import_lines:
            match = re.match(r"from ([\w\.]+) import (.+)", line)
            if not match:
                continue

            module_path, symbols = match.groups()
            symbol_list = [s.strip() for s in symbols.split(",")]
            try:
                mod_parts = module_path.split(".")
                base_dir = Path(self.symbol_service.root_path).resolve()
                for part in mod_parts:
                    base_dir = base_dir / part
                if base_dir.with_suffix(".py").exists():
                    module_file = base_dir.with_suffix(".py")
                    src = module_file.read_text(encoding="utf-8")
                    for symbol in symbol_list:
                        if symbol in src:
                            resolved[symbol] = {
                                "file": str(module_file),
                                "source": src,
                                "module_import_path": module_path + "." + symbol
                            }
            except Exception:
                continue

        return resolved
