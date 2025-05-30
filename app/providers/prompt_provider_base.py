from __future__ import annotations
from abc import abstractmethod
from sqlalchemy.orm import Session
from pathlib import Path

from app.db.models import AgentPrompt, SystemPrompt
from app.providers.base_provider import BaseProvider
from app.factories.context_provider_factory import ContextProviderFactory


class PromptProviderBase(BaseProvider):
    """Base class for prompt generators with optional context/agent/system loading."""

    def __init__(self, config, engine=None):
        super().__init__(config=config, engine=engine)

        self._agent_prompt = None
        self._system_prompt = None
        self._context_provider = None

        if not self.config or not self._engine:
            return

        with Session(bind=self._engine) as session:
            if agent_id := self.config.config.get("agent_prompt_id"):
                self._agent_prompt = session.get(AgentPrompt, agent_id)

            if system_id := self.config.config.get("system_prompt_id"):
                self._system_prompt = session.get(SystemPrompt, system_id)

            if context_id := self.config.config.get("context_provider_id"):
                self._context_provider = ContextProviderFactory.create(id=context_id)

    def _run_provider(self, input: dict) -> str:
        return self._run(input)

    @abstractmethod
    def _run(self, input: dict) -> str:
        raise NotImplementedError
