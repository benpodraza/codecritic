from __future__ import annotations

from abc import abstractmethod
from app.providers.base_provider import BaseProvider
from app.providers.context_provider_base import ContextProviderBase
from app.providers.tool_provider_base import ToolProviderBase

class ScoreProviderBase(BaseProvider):
    """Base class for score providers."""

    def _run_provider(self, input: dict) -> str:
        return self._run(input)
    
    def set_context_provider(self, provider: ContextProviderBase) -> None:
        self.context_provider = provider

    def set_tool_provider(self, provider: ToolProviderBase) -> None:
        if not hasattr(self, "tool_providers"):
            self.tool_providers = []
        self.tool_providers.append(provider)

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
