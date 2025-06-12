from __future__ import annotations
from abc import abstractmethod
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.models import AgentPrompt, SystemPrompt
from app.db.schemas import PromptOutputSchema
from app.providers.base_provider import BaseProvider
from app.factories.context_provider_factory import ContextProviderFactory


class PromptProviderBase(BaseProvider):
    """Base class for prompt generators with optional context/agent/system loading."""

    def __init__(
        self,
        config,
        called_by_type=None,
        called_by_id=None,
        agent_text=None,
        system_text=None,
        context_provider=None,
    ):
        super().__init__(config=config, called_by_type=called_by_type, called_by_id=called_by_id)

        self.agent_text = agent_text
        self.system_text = system_text
        self._context_provider = context_provider

    def _run_provider(self, input: dict) -> PromptOutputSchema:
        return self._run(input)

    @abstractmethod
    def _run(self, input: dict) -> PromptOutputSchema:
        raise NotImplementedError