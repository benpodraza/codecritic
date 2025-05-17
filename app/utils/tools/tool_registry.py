"""
ToolRegistry: Central dispatcher for running static analysis, formatting, or code-quality tools.
"""

from typing import Callable, Dict


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable[[str], str]] = {}

    def register(self, name: str, fn: Callable[[str], str]):
        """Register a tool by name."""
        self._tools[name] = fn

    def run(self, name: str, code: str) -> str:
        """Run a registered tool."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not registered.")
        return self._tools[name](code)

    def list_tools(self) -> list[str]:
        """List available tool names."""
        return list(self._tools.keys())
