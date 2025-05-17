import os
import textwrap
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor
from app.utils.patch_agent.patch_agent import PatchAgent  # adjust import path as needed

class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return f"# fake patch output for prompt:\n{prompt[:40]}..."


def test_patch_agent_run_basic(tmp_path):
    # 1. Inject dummy API key
    os.environ["OPENAI_API_KEY"] = "fake-key"

    # 2. Prepare example input file
    example_code = textwrap.dedent("""
        # === AI-FIRST METADATA ===
        # author: test
        # purpose: patch agent test

        def add(a, b):
            return a + b
    """).strip()
    input_file = tmp_path / "inputs" / "test_patch.py"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(example_code, encoding="utf-8")

    # 3. Load patch agent prompt template (no Jinja includes)
    from jinja2 import Template as JinjaTemplate

    prompt_path = Path("app/utils/patch_agent/patch_agent.txt")
    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_template = JinjaTemplate(prompt_text)

    # 4. Instantiate patch agent
    symbol_service = SymbolService(tmp_path)
    context_provider = ContextProviderPreprocessor(symbol_service)
    tool_provider = ToolProviderPreprocessor()
    engine = FakeEngine()

    agent = PatchAgent(
        context_provider=context_provider,
        tool_provider=tool_provider,
        engine=engine,
        model_payload={"model": "gpt-4", "temperature": "0.2"},
        prompt_template=prompt_template
    )

    # 5. Run the patch agent
    result = agent.run({
        "symbol": "add",
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
    # PatchAgent may or may not return tools, but response must be non-empty
    assert len(result["response"]) > 0
