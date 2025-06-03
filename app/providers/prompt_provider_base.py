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

    def __init__(self, config, called_by_type=None, called_by_id=None):
        super().__init__(config=config, called_by_type=called_by_type, called_by_id=called_by_id)

        self._agent_prompt = None
        self._system_prompt = None
        self._context_provider = None
        self.agent_text = None
        self.system_text = None

        if not self._config or not self._engine:
            return

        with Session(bind=self._engine) as session:
            if agent_id := self._config.config.get("agent_prompt_id"):
                self._agent_prompt = session.get(AgentPrompt, agent_id)
                if self._agent_prompt:
                    self.agent_text = Path("extensions") / self._agent_prompt.artifact_path
                    self.agent_text = self.agent_text.read_text(encoding="utf-8").strip()

            if system_id := self._config.config.get("system_prompt_id"):
                self._system_prompt = session.get(SystemPrompt, system_id)
                if self._system_prompt:
                    self.system_text = Path("extensions") / self._system_prompt.artifact_path
                    self.system_text = self.system_text.read_text(encoding="utf-8").strip()

            if context_id := self._config.config.get("context_provider_id"):
                self._context_provider = ContextProviderFactory.create(id=context_id)

    def _run_provider(self, input: dict) -> PromptOutputSchema:
        return self._run(input)

    @abstractmethod
    def _run(self, input: dict) -> PromptOutputSchema:
        raise NotImplementedError
