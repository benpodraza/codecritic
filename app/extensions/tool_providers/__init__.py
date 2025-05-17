from .dummy_tool_provider import DummyToolProvider
from .black_runner import BlackToolProvider
from .mypy_runner import MypyToolProvider
from .radon_runner import RadonToolProvider
from .ruff_runner import RuffToolProvider
from ...registries.tool_providers import TOOL_PROVIDER_REGISTRY

TOOL_PROVIDER_REGISTRY.register("dummy", DummyToolProvider)
TOOL_PROVIDER_REGISTRY.register("black", BlackToolProvider)
TOOL_PROVIDER_REGISTRY.register("mypy", MypyToolProvider)
TOOL_PROVIDER_REGISTRY.register("radon", RadonToolProvider)
TOOL_PROVIDER_REGISTRY.register("ruff", RuffToolProvider)

__all__ = [
    "DummyToolProvider",
    "BlackToolProvider",
    "MypyToolProvider",
    "RadonToolProvider",
    "RuffToolProvider",
]
