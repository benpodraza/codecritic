from __future__ import annotations
from abc import abstractmethod
from app.providers.base_provider import BaseProvider

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.providers.context_provider_base import ContextProviderBase
    from app.providers.score_provider_base import ScoreProviderBase


from app.db.schemas import ToolOutputSchema

class ToolProviderBase(BaseProvider):
    """Base class for tool providers with optional context/score wiring."""

    def _run_provider(self, input: dict) -> ToolOutputSchema:
        output = self._run(input)

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
    def _run(self, input: dict) -> ToolOutputSchema:
        raise NotImplementedError

