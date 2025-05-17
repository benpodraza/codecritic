from abc import ABC, abstractmethod
from typing import Any

class AgentEngineRunner(ABC):
    @abstractmethod
    def call_engine(self, prompt: str, config: dict[str, Any]) -> str:
        """
        Call the underlying LLM engine with the given prompt and configuration.

        Args:
            prompt (str): Full LLM prompt.
            config (dict): Parameters like model, temperature, system_role, etc.

        Returns:
            str: The LLM-generated response.
        """
        pass