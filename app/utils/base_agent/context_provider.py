"""
ContextProvider: Interface for generating prompt context inputs.

Implemented per-agent to resolve any context references
(e.g. children functions, imports, metadata).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ContextProvider(ABC):
    """
    Abstract base for agent-level context expansion.
    """

    @abstractmethod
    def get_context(self, inputs: dict[str, Any]) -> dict:
        """
        Resolve and return a context dictionary for prompt formatting.

        Args:
            inputs: Agent input parameters (e.g., symbol, file)

        Returns:
            dict: Fully formed prompt context
        """
        pass
