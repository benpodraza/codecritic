from __future__ import annotations

from abc import abstractmethod

from app.db.schemas import ContextOutputSchema
from app.enums.logging_enums import RunContext
from app.providers.base_provider import BaseProvider

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.providers.score_provider_base import ScoreProviderBase
    from app.providers.tool_provider_base import ToolProviderBase

class ContextProviderBase(BaseProvider):
    def __init__(self, config=None, context: RunContext = None, **kwargs):
        super().__init__(config=config, context=context, **kwargs)

    def _run_provider(self, input: dict) -> ContextOutputSchema:
        return self._run(input=input, context=self.fork_context())
    
    def set_tool_provider(self, provider: "ToolProviderBase") -> None:
        if not hasattr(self, "tool_providers"):
            self.tool_providers = []
        self.tool_providers.append(provider)

    def set_score_provider(self, provider: "ScoreProviderBase") -> None:
        self.score_provider = provider


    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> ContextOutputSchema:
        raise NotImplementedError
