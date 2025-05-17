import builtins
import types
import sys

import pydantic
import pytest

# Patch a minimal `openai` module so schemas importing from openai work
@pytest.fixture(autouse=True)
def dummy_openai(monkeypatch):
    # Create a fake openai module
    fake_openai = types.SimpleNamespace(OpenAIClient=object)
    # Inject it into sys.modules so 'import openai' just returns our fake
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    return fake_openai

from app.enums.state_transition_enums import TransitionReason
from app.schemas.shared_config_schemas import ModelEngine, PromptVariant
from app.schemas.agent_config_schema import AgentConfig
from app.schemas.experiment_config_schemas import (
    ExperimentConfig, EvaluatorConfig, SystemType, CodeStyle, ScoringModel
)
from app.schemas.state_management_schemas import StateTransitionLog


def test_agent_config_instantiation():
    cfg = AgentConfig(
        name="PatchAgent",
        engine=ModelEngine.GPT_4O,
        engine_config={"model": "gpt-4o"},
        prompt_variant=PromptVariant.ZERO_SHOT,
        base_prompt_path="/tmp/prompt.txt",
    )
    assert cfg.name == "PatchAgent"
    assert cfg.engine is ModelEngine.GPT_4O


def test_experiment_config_and_state_log(tmp_path):
    agent_cfg = AgentConfig(
        name="GeneratorAgent",
        engine=ModelEngine.GPT_4O,
        engine_config={},
        prompt_variant=PromptVariant.ZERO_SHOT,
        base_prompt_path=str(tmp_path / "p.txt"),
    )
    exp_cfg = ExperimentConfig(
        experiment_id="e1",
        run_id="r1",
        system=SystemType.PREPROCESSING,
        description="desc",
        code_style=CodeStyle.AI_FIRST,
        max_lines_per_function=10,
        generator=agent_cfg,
        discriminator=None,
        mediator=None,
        patchor=None,
        recommender=None,
        evaluator=EvaluatorConfig(name="eval", version="v1"),
        scoring_model=ScoringModel.HEURISTIC_V1,
    )
    assert exp_cfg.experiment_id == "e1"

    log = StateTransitionLog(
        experiment_id="e1", 
        symbol="foo",
        round=1,
        from_agent=None,
        to_agent="GENERATE",
        reason=TransitionReason.FIRST_ROUND,
        timestamp="2025-01-01T00:00:00Z"
    )

    assert log.experiment_id == "e1"
