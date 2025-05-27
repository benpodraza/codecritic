from __future__ import annotations
from abc import abstractmethod
from app.providers.base_provider import BaseProvider

class AgentEngineProviderBase(BaseProvider):
    """Base class for agent engines that return raw LLM output."""

    def _run_provider(self, input: dict) -> str:
        # Only responsible for calling the underlying engine
        return self._run(input)

    @abstractmethod
    def _run(self, input: dict) -> str:
        """Implement this to call the actual LLM engine (e.g., OpenAI GPT-4o)."""
        raise NotImplementedError
