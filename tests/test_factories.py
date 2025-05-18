from importlib import import_module

from app.factories.agent import AgentFactory
from app.factories.system_manager import SystemManagerFactory
from app.factories.state_manager import StateManagerFactory
from app.factories.prompt_manager import PromptGeneratorFactory
from app.factories.tool_provider import ToolProviderFactory
from app.factories.scoring_provider import ScoringProviderFactory
from app.factories.context_provider import ContextProviderFactory


from tests.test_bootstrap import load_all_extensions


_def_extensions_loaded = False


def _ensure_loaded():
    global _def_extensions_loaded
    if not _def_extensions_loaded:
        load_all_extensions()
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


def test_context_provider_factory():
    _ensure_loaded()
    provider = ContextProviderFactory.create("dummy")
    assert provider.get_context() == {}


def test_prompt_generator_factory():
    _ensure_loaded()
    provider = ContextProviderFactory.create("dummy")
    generator = PromptGeneratorFactory.create("basic", context_provider=provider)
    assert isinstance(generator.generate_prompt({}, {}), str)


def test_tool_provider_factory():
    _ensure_loaded()
    provider = ToolProviderFactory.create("dummy")
    assert provider.run() is True


def test_scoring_provider_factory():
    _ensure_loaded()
    provider = ScoringProviderFactory.create("dummy")
    assert provider.score() == 0


def test_basic_scoring_provider_factory():
    _ensure_loaded()
    provider = ScoringProviderFactory.create("basic")
    result = provider.score(
        {
            "evaluation": [],
            "code_quality": [],
            "conversation": [],
            "prompt": [],
            "state": [],
        }
    )
    assert isinstance(result, dict)
