# app/schemas/tool_result_schema.py

from typing import Any, Dict
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """
    Unified result schema for any tool runner (formatters, linters, analyzers).

    Attributes:
        tool: Name of the tool (e.g., "black", "ruff", "mypy")
        status: One of "success", "error", "skipped"
        output: Raw stdout (or final formatted code) returned by the tool
        metadata: Structured diagnostics, length, error details, or metrics
    """

    tool: str = Field(..., description="Name of the tool (e.g., black, ruff, mypy)")
    status: str = Field(..., description="Status: success, error, skipped")
    output: str = Field(..., description="Raw stdout or final formatted code")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Structured diagnostics or metrics")
