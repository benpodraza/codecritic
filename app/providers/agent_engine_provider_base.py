from __future__ import annotations

from abc import abstractmethod
from app.providers.base_provider import BaseProvider

class AgentEngineProviderBase(BaseProvider):
    """Base class for agent engine providers (e.g., OpenAI, Anthropic, etc.)."""

    def _run_provider(self, input: dict) -> str:
        return self._run(input)

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
