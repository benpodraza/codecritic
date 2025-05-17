import os
import textwrap
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader

from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor
from app.systems.preprocessing.agents.discriminator.discriminator_agent import DiscriminatorAgent

class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return f"# fake discriminator verdict for prompt:\n{prompt[:40]}..."

def test_discriminator_agent_run_basic(tmp_path):
    os.environ["OPENAI_API_KEY"] = "fake-key"

    # Prepare input file
    example_code = textwrap.dedent("""
        # === AI-FIRST METADATA ===
        # author: test
        # purpose: test prompt generation

        def hello():
            print('hello world')
    """).strip()
    input_file = tmp_path / "inputs" / "hello_test.py"
    input_file.parent.mkdir(parents=True)
    input_file.write_text(example_code, encoding="utf-8")

    # Load and render prompt
    prompt_path = Path("app/systems/preprocessing/agents/discriminator/prompts/discriminator.txt")
    env = Environment(loader=FileSystemLoader(str(prompt_path.parent)))
    template = env.get_template(prompt_path.name)

    context = ContextProviderPreprocessor(SymbolService(tmp_path))._build_context("hello", input_file)

    agent = DiscriminatorAgent(
        context_provider=ContextProviderPreprocessor(SymbolService(tmp_path)),
        tool_provider=ToolProviderPreprocessor(),
        engine=FakeEngine(),
        model_payload={"model": "gpt-4", "temperature": "0.2"},
        prompt_template=template.render(**context)
    )

    result = agent.run({
        "symbol": "hello",
        "file": str(input_file),
        "experiment_id": "exp-id",
        "run_id": "run-001",
        "round": 1,
        "system": "PREPROCESSING",
        "log_path": tmp_path / "logs"
    })

    assert "prompt" in result
    assert "response" in result
    assert isinstance(result["response"], str)
    # discriminator may return a score field, for example:
    assert "score" in result or "response" in result
