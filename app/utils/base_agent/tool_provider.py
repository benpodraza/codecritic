from abc import ABC, abstractmethod
from typing import Dict


class ToolProvider(ABC):
    """
    Abstract interface for accessing tool-enhanced variants of code.

    Examples:
        - Lint with ruff
        - Format with black
        - Analyze with pyrefactor
    """

    @abstractmethod
    def run_all(self, code: str) -> str:
        """Run all enabled tools on the given code string."""
        pass

    @abstractmethod
    def run_tool(self, name: str, code: str) -> str:
        """Run a specific tool by name."""
        pass

    @abstractmethod
    def list_tools(self) -> Dict[str, str]:
        """List available tools and short descriptions."""
        pass
