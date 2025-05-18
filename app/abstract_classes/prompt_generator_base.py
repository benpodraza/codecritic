from __future__ import annotations

from abc import ABC, abstractmethod

from ..factories.logging_provider import LoggingMixin, LoggingProvider


class PromptGeneratorBase(LoggingMixin, ABC):
    """Base class for generating prompts."""

    def __init__(self, logger: LoggingProvider | None = None) -> None:
        super().__init__(logger)

    def generate_prompt(self, *args, **kwargs) -> str:
        self._log.debug("Prompt generation start")
        prompt = self._generate_prompt(*args, **kwargs)
        self._log.debug("Prompt generation end")
        return prompt

    @abstractmethod
    def _generate_prompt(self, *args, **kwargs) -> str:
        """Return a generated prompt."""
        raise NotImplementedError
