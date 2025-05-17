from .. import Registry

PROMPT_GENERATOR_REGISTRY = Registry()

try:  # pragma: no cover - optional seed import
    from ...extensions.prompt_generators.dummy_prompt_generator import (
        DummyPromptGenerator,
    )

    PROMPT_GENERATOR_REGISTRY.register("dummy", DummyPromptGenerator)
except Exception:  # pragma: no cover - ignore failures during optional import
    pass
