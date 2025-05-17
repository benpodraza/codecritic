from .dummy_prompt_generator import DummyPromptGenerator
from ...registries.prompt_generators import PROMPT_GENERATOR_REGISTRY

PROMPT_GENERATOR_REGISTRY.register("dummy", DummyPromptGenerator)

__all__ = ["DummyPromptGenerator"]
