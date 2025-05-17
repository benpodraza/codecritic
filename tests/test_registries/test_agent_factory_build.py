import os
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Set BEFORE imports to avoid import-time errors
os.environ["OPENAI_API_KEY"] = "fake-key"

# Imports after setting environment variable
from app.utils.agents.agent_factory.registry_factory import build_agent
from app.utils.symbol_graph.symbol_service import SymbolService
from app.enums.agent_management_enums import AgentRole
from app.schemas.agent_config_schema import AgentConfig
from app.schemas.shared_config_schemas import ModelEngine, PromptVariant

@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    # Mock OpenAI client to avoid actual API calls
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="fake-response"))]
    )

    # Patch the exact import used in openai_gpt4o_runner.py
    monkeypatch.setattr(
        "app.utils.agents.engine.openai_gpt4o_runner.client",
        mock_openai_client
    )

    # Mock Jinja2 Template rendering
    mock_template = MagicMock()
    mock_template.render.return_value = "fake-prompt"
    mock_env = MagicMock()
    mock_env.get_template.return_value = mock_template
    monkeypatch.setattr(
        "app.utils.agents.agent_factory.registry_factory.Environment",
        MagicMock(return_value=mock_env)
    )

    # Mock PreprocessingToolProvider if needed
    mock_tool_provider = MagicMock()
    monkeypatch.setattr(
        "app.tool_providers.preprocessing_tool_provider.PreprocessingToolProvider",
        MagicMock(return_value=mock_tool_provider)
    )

def test_build_agent_success(tmp_path):
    symbol_service = SymbolService(tmp_path)
    agent = build_agent('generator', symbol_service)

    assert agent is not None
    assert agent.engine is not None
    assert agent.engine.call_engine("prompt", {}) == "fake-response"
    assert agent.prompt_template.render() == "fake-prompt"

def test_build_agent_missing_engine(tmp_path):
    symbol_service = SymbolService(tmp_path)

    bad_config = AgentConfig(
        name="test_agent",
        engine=ModelEngine.CUSTOM,
        engine_config={"temperature": "0.2"},
        prompt_variant=PromptVariant.ZERO_SHOT,
        base_prompt_path="app/prompts/base/ai_first_base.txt"
    )

    # Temporarily mock ModelEngine's runner_class property to return None
    original_runner_class = ModelEngine.runner_class

    def mock_runner_class(self):
        return None

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(ModelEngine, "runner_class", property(mock_runner_class))

        with pytest.raises(ValueError, match="Engine runner not defined"):
            build_agent(
                agent_key='generator',
                symbol_service=symbol_service
            )

    # Restore original runner_class property
    ModelEngine.runner_class = original_runner_class
