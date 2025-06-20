from __future__ import annotations
from abc import abstractmethod
from copy import deepcopy
from typing import TYPE_CHECKING

from app.enums.logging_enums import RunContext
from app.providers.base_provider import BaseProvider
from app.db.schemas import ToolOutputSchema

if TYPE_CHECKING:
    from app.providers.context_provider_base import ContextProviderBase
    from app.providers.score_provider_base import ScoreProviderBase


class ToolProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        context_provider: ContextProviderBase | None = None,
        score_provider: ScoreProviderBase | None = None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self._context_provider = context_provider
        self._score_provider = score_provider

    def _run_provider(self, input: dict) -> ToolOutputSchema:
        # ✅ Explicitly pass self._context
        output = self._run(input=input, context=self.fork_context())

        if not isinstance(output, ToolOutputSchema):
            raise TypeError(f"Expected ToolOutputSchema, got {type(output).__name__}")
        if output.return_code is None:
            raise ValueError("Tool output is missing `return_code`")
        if output.summary is None:
            output.summary = "⚠️ Missing summary"
        if output.metrics is None:
            output.metrics = {}

        return output

    def set_context_provider(self, provider: ContextProviderBase) -> None:
        self.context_provider = provider

    def set_score_provider(self, provider: ScoreProviderBase) -> None:
        self.score_provider = provider

    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> ToolOutputSchema:
        raise NotImplementedError
