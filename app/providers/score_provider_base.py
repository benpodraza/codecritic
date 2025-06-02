from __future__ import annotations

from abc import abstractmethod
from app.providers.base_provider import BaseProvider
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.providers.context_provider_base import ContextProviderBase
    from app.providers.tool_provider_base import ToolProviderBase

from app.db.schemas import ScoreOutputSchema

class ScoreProviderBase(BaseProvider):
    """Base class for score providers."""

    def _run_provider(self, input: dict) -> ScoreOutputSchema:
        return self._run(input)

    def set_context_provider(self, provider: ContextProviderBase) -> None:
        self.context_provider = provider

    def set_tool_provider(self, provider: ToolProviderBase) -> None:
        if not hasattr(self, "tool_providers"):
            self.tool_providers = []
        self.tool_providers.append(provider)

    @abstractmethod
    def _run(self, input: dict) -> ScoreOutputSchema:
        raise NotImplementedError