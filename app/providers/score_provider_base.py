from __future__ import annotations
from abc import abstractmethod
from copy import deepcopy
from app.enums.logging_enums import RunContext
from app.providers.base_provider import BaseProvider
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.providers.context_provider_base import ContextProviderBase
    from app.providers.tool_provider_base import ToolProviderBase

from app.db.schemas import ScoreOutputSchema

class ScoreProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        context_provider=None,
        tool_providers=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self._context_provider = context_provider
        self._tool_providers = tool_providers or []

    def _run_provider(self, input: dict) -> ScoreOutputSchema:
        caller = self._context.called_by_type.name if self._context and self._context.called_by_type else "UNKNOWN"
        print(f"🛠️ ScoreProvider called by: {caller}")
        return self._run(input=input, context=self.fork_context())

    def set_context_provider(self, provider: ContextProviderBase) -> None:
        self.context_provider = provider

    def set_tool_provider(self, provider: ToolProviderBase) -> None:
        if not hasattr(self, "tool_providers"):
            self.tool_providers = []
        self.tool_providers.append(provider)

    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> ScoreOutputSchema:
        raise NotImplementedError
