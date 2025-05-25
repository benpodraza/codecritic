from __future__ import annotations

from abc import abstractmethod
from app.providers.base_provider import BaseProvider
from app.providers.score_provider_base import ScoreProviderBase
from app.providers.tool_provider_base import ToolProviderBase

class ContextProviderBase(BaseProvider):
    """Base class for context providers."""

    def _run_provider(self, input: dict) -> str:
        return self._run(input)
    
    def set_tool_provider(self, provider: ToolProviderBase) -> None:
        if not hasattr(self, "tool_providers"):
            self.tool_providers = []
        self.tool_providers.append(provider)

    def set_score_provider(self, provider: ScoreProviderBase) -> None:
        self.score_provider = provider


    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
