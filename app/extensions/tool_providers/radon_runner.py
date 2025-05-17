from __future__ import annotations
from pathlib import Path
from ...abstract_classes.tool_provider_base import ToolProviderBase
from radon.complexity import cc_visit


class RadonToolProvider(ToolProviderBase):
    def _run(self, target: str):
        file_path = Path(target)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {target}")

        code = file_path.read_text(encoding="utf-8", errors="ignore")
        complexity_blocks = cc_visit(code)
        result = [
            {"name": blk.name, "complexity": blk.complexity, "lineno": blk.lineno}
            for blk in complexity_blocks
        ]
        return result
