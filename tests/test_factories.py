from importlib import import_module

from app.factories.agent import AgentFactory
from app.factories.system_manager import SystemManagerFactory
from app.factories.state_manager import StateManagerFactory
from app.factories.prompt_manager import PromptGeneratorFactory
from app.factories.tool_provider import ToolProviderFactory
from app.factories.scoring_provider import ScoringProviderFactory


def _load_extensions():
    import_module("app.extensions.agents")
    import_module("app.extensions.system_managers")
    import_module("app.extensions.state_managers")
    import_module("app.extensions.prompt_generators")
    import_module("app.extensions.context_providers")
    import_module("app.extensions.tool_providers")
    import_module("app.extensions.scoring_models")


_def_extensions_loaded = False


def _ensure_loaded():
    global _def_extensions_loaded
    if not _def_extensions_loaded:
        _load_extensions()
        _def_extensions_loaded = True


def test_agent_factory():
    _ensure_loaded()
    agent = AgentFactory.create("dummy")
    assert agent is not None


def test_system_manager_factory():
    _ensure_loaded()
    manager = SystemManagerFactory.create("dummy")
    assert manager is not None


def test_state_manager_factory():
    _ensure_loaded()
    manager = StateManagerFactory.create("dummy")
    assert manager is not None


def test_prompt_generator_factory():
    _ensure_loaded()
    generator = PromptGeneratorFactory.create("dummy")
    assert generator.generate_prompt() == "dummy prompt"


def test_tool_provider_factory():
    _ensure_loaded()
    provider = ToolProviderFactory.create("dummy")
    assert provider.run() is True


def test_scoring_provider_factory():
    _ensure_loaded()
    provider = ScoringProviderFactory.create("dummy")
    assert provider.score() == 0
