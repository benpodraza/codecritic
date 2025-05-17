import os
import textwrap
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor
from app.systems.preprocessing.agents.generator.generator_agent import GeneratorAgent

class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return f"# fake transformed output for prompt:\n{prompt[:40]}..."

def test_generator_agent_run_with_jinja_template(tmp_path):
    os.environ["OPENAI_API_KEY"] = "fake-key"

    # Create minimal input file
    example_code = textwrap.dedent("""
        # === AI-FIRST METADATA ===
        # author: test
        # purpose: test prompt generation

        def hello():
            print('hello world')
    """).strip()

    input_file = tmp_path / "inputs" / "hello_test.py"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(example_code, encoding="utf-8")

    # Load and render prompt template using Jinja2
    prompt_path = Path("app/systems/preprocessing/agents/generator/prompts/zero_shot.txt")
    env = Environment(loader=FileSystemLoader(str(prompt_path.parent)))
    template = env.get_template(prompt_path.name)

    # Build context manually
    symbol_service = SymbolService(tmp_path)
    context_provider = ContextProviderPreprocessor(symbol_service)
    tool_provider = ToolProviderPreprocessor()
    engine = FakeEngine()

    agent = GeneratorAgent(
        context_provider=context_provider,
        tool_provider=tool_provider,
        engine=engine,
        model_payload={"model": "gpt-4", "temperature": "0.2"},
        prompt_template=template
    )

    result = agent.run({
        "symbol": "hello",
        "file": str(input_file),
        "experiment_id": "unit-test-exp",
        "run_id": "run-001",
        "round": 1,
        "system": "PREPROCESSING",
        "log_path": tmp_path / "logs"
    })

    assert "prompt" in result
    assert "response" in result
    assert "tools" in result
    assert isinstance(result["response"], str)
