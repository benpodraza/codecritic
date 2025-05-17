from pathlib import Path
from typing import Any, Dict

import pytest

from app.utils.base_agent.base_agent import BaseAgent
from app.utils.engine.agent_engine_runner import AgentEngineRunner


class DummyContextProvider:
    def get_context(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"name": "world"}


class DummyEngine(AgentEngineRunner):
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def call_engine(self, prompt: str, config: dict[str, Any]) -> str:
        if self.should_fail:
            raise RuntimeError("fail")
        return prompt.upper()


class DummyAgent(BaseAgent):
    pass


def test_base_agent_run_success(tmp_path):
    log_file = tmp_path / "log.jsonl"
    agent = DummyAgent(
        name="Dummy",
        prompt_template="hello {name}",
        context_provider=DummyContextProvider(),
        tool_provider=None,
        model_payload={"model": "dummy"},
        engine=DummyEngine(),
    )
    result = agent.run({
        "experiment_id": "e1",
        "run_id": "r1",
        "round": 1,
        "system": "TEST",
        "symbol": "sym",
        "log_path": log_file,
    })

    assert result["agent"] == "Dummy"
    assert agent.state.name == "COMPLETED"
    assert log_file.exists()


def test_base_agent_run_error(tmp_path):
    log_file = tmp_path / "err.jsonl"
    agent = DummyAgent(
        name="Dummy",
        prompt_template="hello {name}",
        context_provider=DummyContextProvider(),
        tool_provider=None,
        model_payload={"model": "dummy"},
        engine=DummyEngine(should_fail=True),
    )
    with pytest.raises(RuntimeError):
        agent.run({
            "experiment_id": "e1",
            "run_id": "r1",
            "round": 1,
            "system": "TEST",
            "symbol": "sym",
            "log_path": log_file,
        })
    assert log_file.exists()
