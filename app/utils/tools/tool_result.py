from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ToolResult:
    """
    Unified result schema for any tool runner (formatters, linters, analyzers).

    Attributes:
        tool: Name of the tool (e.g., "black", "ruff", "mypy")
        status: One of "success", "error", "skipped"
        output: Raw stdout (or final formatted code) returned by the tool
        metadata: Structured diagnostics, length, error details, or metrics
    """
    tool: str
    status: str
    output: str
    metadata: Dict[str, Any]
