from __future__ import annotations

import logging
from abc import ABC, abstractmethod


class PromptGeneratorBase(ABC):
    """Base class for generating prompts."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_prompt(self, *args, **kwargs) -> str:
        self.logger.debug("Prompt generation start")
        prompt = self._generate_prompt(*args, **kwargs)
        self.logger.debug("Prompt generation end")
        return prompt

    @abstractmethod
    def _generate_prompt(self, *args, **kwargs) -> str:
        """Return a generated prompt."""
        raise NotImplementedError
