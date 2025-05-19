from app.factories.agent import AgentFactory
from app.factories.system_manager import SystemManagerFactory
from app.factories.state_manager import StateManagerFactory
from app.factories.prompt_manager import PromptGeneratorFactory
from app.factories.tool_provider import ToolProviderFactory
from app.factories.scoring_provider import ScoringProviderFactory
from app.factories.context_provider import ContextProviderFactory
from app.factories.logging_provider import CodeQualityLog, RecommendationLog


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
    assert isinstance(generator.generate_prompt({}, {}, "test_experiment", 0), str)


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


def test_advanced_scoring_provider_factory():
    _ensure_loaded()
    provider = ScoringProviderFactory.create("advanced")
    result = provider.score(
        {
            "code_quality": [
                CodeQualityLog(
                    experiment_id="exp",
                    round=0,
                    symbol="mod",
                    lines_of_code=10,
                    cyclomatic_complexity=5.0,
                    maintainability_index=80.0,
                    lint_errors=0,
                )
            ],
            "recommendation": [
                RecommendationLog(
                    experiment_id="exp",
                    round=0,
                    symbol="mod",
                    file_path="mod.py",
                    line_start=0,
                    line_end=0,
                    recommendation="{}",
                    context="ctx",
                )
            ],
        },
        experiment_id="exp",
    )
    assert result["maintainability_index"] == 80.0
    assert result["cyclomatic_complexity"] == 5.0
    assert result["recommendation_quality"] == 1.0
