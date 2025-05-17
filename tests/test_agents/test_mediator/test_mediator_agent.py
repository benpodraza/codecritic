import os
import textwrap
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import pytest

from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor
from app.systems.preprocessing.agents.mediator.mediator_agent import MediatorAgent

class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return f"# fake mediator output for prompt:\n{prompt[:40]}..."


def test_mediator_agent_run_basic(tmp_path):
    # 1. Inject dummy API key
    os.environ["OPENAI_API_KEY"] = "fake-key"

    # 2. Prepare example input file
    example_code = textwrap.dedent("""
        # === AI-FIRST METADATA ===
        # author: test
        # purpose: mediator test

        def hello():
            print('hello from mediator')
    """).strip()
    input_file = tmp_path / "inputs" / "hello_mediate.py"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(example_code, encoding="utf-8")

    # 3. Load and render mediator prompt template
    prompt_path = Path("app/systems/preprocessing/agents/mediator/prompts/mediator.txt")
    env = Environment(loader=FileSystemLoader(str(prompt_path.parent)))
    template = env.get_template(prompt_path.name)
    context = ContextProviderPreprocessor(SymbolService(tmp_path))._build_context("hello", input_file)
    prompt_str = template.render(**context)

    # 4. Instantiate mediator agent
    agent = MediatorAgent(
        context_provider=ContextProviderPreprocessor(SymbolService(tmp_path)),
        tool_provider=ToolProviderPreprocessor(),
        engine=FakeEngine(),
        model_payload={"model": "gpt-4", "temperature": "0.2"},
        prompt_template=prompt_str
    )

    # 5. Run the mediator agent
    result = agent.run({
        "symbol": "hello",
        "file": str(input_file),
        "experiment_id": "exp-id",
        "run_id": "run-001",
        "round": 1,
        "system": "PREPROCESSING",
        "log_path": tmp_path / "logs"
    })

    # 6. Assert outputs
    assert "prompt" in result
    assert "response" in result
    assert isinstance(result["response"], str)
    # Mediator returns collected responses or merged context
    assert "tools" in result
