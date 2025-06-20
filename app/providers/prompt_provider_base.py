from __future__ import annotations
from abc import abstractmethod

from app.db.models import AgentPrompt, SystemPrompt
from app.db.schemas import AgentEngineExtraction, PromptOutputSchema
from app.enums.logging_enums import RunContext
from app.providers.base_provider import BaseProvider
from app.factories.context_provider_factory import ContextProviderFactory


class PromptProviderBase(BaseProvider):
    def __init__(
        self,
        config=None,
        agent_text=None,
        system_text=None,
        context_provider=None,
        context: RunContext = None,
        **kwargs
    ):
        super().__init__(config=config, context=context, **kwargs)
        self.agent_text = agent_text
        self.system_text = system_text
        self._context_provider = context_provider

    def _run_provider(self, input: dict) -> PromptOutputSchema:
        result = self._run(input=input, context=self.fork_context())
        return result

    @abstractmethod
    def _run(self, input: dict, context: RunContext | None = None) -> PromptOutputSchema:
        raise NotImplementedError
    
    @abstractmethod
    def _extract(self, response: str) -> AgentEngineExtraction:
        raise NotImplementedError
