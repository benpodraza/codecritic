import os
import textwrap
from pathlib import Path
from jinja2 import Template as JinjaTemplate

from app.utils.recommender_agent.recommender_agent import RecommenderAgent
from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor


def test_recommender_agent_run_basic(tmp_path):
    # Mock API key
    os.environ["OPENAI_API_KEY"] = "fake-key"

    # Prepare example code and write to input file
    example_code = textwrap.dedent("""
        # === AI-FIRST METADATA ===
        # author: test
        # purpose: recommendation test

        def hello():
            print('hello for recommender')
    """).strip()
    input_file = tmp_path / "inputs" / "test_recommender.py"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(example_code, encoding="utf-8")

    # Load prompt template
    prompt_path = Path("app/utils/recommender_agent/recommender_agent.txt")
    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_template = JinjaTemplate(prompt_text)

    # Instantiate dependencies
    symbol_service = SymbolService(tmp_path)
    context_provider = ContextProviderPreprocessor(symbol_service)
    tool_provider = ToolProviderPreprocessor()
    # Fake engine that echoes prompt
    class FakeEngine:
        def call_engine(self, prompt: str, config: dict) -> str:
            return f"# fake recommendation output for prompt:\n{prompt}"
    engine = FakeEngine()

    # Instantiate agent
    agent = RecommenderAgent(
        context_provider=context_provider,
        tool_provider=tool_provider,
        engine=engine,
        model_payload={"model": "gpt-4", "temperature": "0.2"},
        prompt_template=prompt_template
    )

    # Run agent
    result = agent.run({
        "symbol": "hello",
        "file": str(input_file),
        "experiment_id": "exp-id",
        "run_id": "run-001",
        "round": 1,
        "system": "PREPROCESSING",
        "log_path": tmp_path / "logs"
    })

    # Assertions
    assert "prompt" in result
    assert "response" in result
    assert isinstance(result["response"], str)
