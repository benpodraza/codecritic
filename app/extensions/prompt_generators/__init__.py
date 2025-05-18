from .dummy_prompt_generator import DummyPromptGenerator
from .basic_prompt_generator import BasicPromptGenerator
from ...registries.prompt_generators import PROMPT_GENERATOR_REGISTRY

PROMPT_GENERATOR_REGISTRY.register("dummy", DummyPromptGenerator)
PROMPT_GENERATOR_REGISTRY.register("basic", BasicPromptGenerator)

__all__ = ["DummyPromptGenerator", "BasicPromptGenerator"]
