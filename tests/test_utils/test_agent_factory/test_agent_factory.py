import types
import sys
import types
from pathlib import Path

import pytest
import pydantic

from app.schemas.shared_config_schemas import PromptVariant

# Provide dummy openai module for AgentConfig
openai_mod = types.ModuleType("openai")
openai_mod.BaseModel = pydantic.BaseModel
sys.modules.setdefault("openai", openai_mod)

from app.enums.agent_management_enums import AgentRole
from app.schemas.agent_config_schema import AgentConfig
from app.utils.agents.agent_factory.agent_factory import build_agent


class DummyRunner:
    def call_engine(self, prompt: str, config: dict) -> str:
        return "ok"


class DummyEngineRunner(DummyRunner):
    pass


def test_build_agent_prompt_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.schemas.shared_config_schemas.ModelEngine.runner_class",
        property(lambda self: DummyEngineRunner),
        raising=False,
    )
    config = AgentConfig(
        name="gen",
        engine="custom/fine-tune",    # must match one of ModelEngine
        engine_config={"temperature": "0.1"},
        prompt_variant=PromptVariant.ZERO_SHOT,
        base_prompt_path="nonexistent.txt"
    )

    with pytest.raises(FileNotFoundError):
        build_agent(AgentRole.GENERATOR, config, None)

