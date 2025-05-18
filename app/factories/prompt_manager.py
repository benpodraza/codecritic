from __future__ import annotations

from ..registries.prompt_generators import PROMPT_GENERATOR_REGISTRY


class PromptGeneratorFactory:
    @staticmethod
    def register(name: str, cls) -> None:
        try:
            PROMPT_GENERATOR_REGISTRY.register(name, cls)
        except KeyError:
            pass

    @staticmethod
    def create(name: str, **kwargs):
        cls = PROMPT_GENERATOR_REGISTRY.get(name)
        if cls is None:
            raise KeyError(f"Prompt generator {name} not registered")
        return cls(**kwargs)
