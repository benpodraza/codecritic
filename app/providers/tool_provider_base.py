from __future__ import annotations

from abc import abstractmethod
from app.providers.base_provider import BaseProvider
from app.providers.context_provider_base import ContextProviderBase
from app.providers.score_provider_base import ScoreProviderBase

class ToolProviderBase(BaseProvider):
    """Base class for tool providers."""

    def _run_provider(self, input: dict) -> str:
        return self._run(input)
    
    def set_context_provider(self, provider: ContextProviderBase) -> None:
        self.context_provider = provider

    def set_score_provider(self, provider: ScoreProviderBase) -> None:
        self.score_provider = provider


    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
