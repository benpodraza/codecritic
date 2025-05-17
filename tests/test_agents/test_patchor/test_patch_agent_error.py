import os
import textwrap
from pathlib import Path

import pytest
from jinja2 import Template as JinjaTemplate

from app.utils.patch_agent.patch_agent import PatchAgent
from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor


class FailingEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        raise RuntimeError("engine failure")


def test_patch_agent_error_logging(tmp_path):
    os.environ["OPENAI_API_KEY"] = "fake"
    input_file = tmp_path / "inputs" / "test_error.py"
    input_file.parent.mkdir(parents=True, exist_ok=True)
    input_file.write_text(
        textwrap.dedent(
            """
            # === AI-FIRST METADATA ===
            # author: test
            """
        ).strip(),
        encoding="utf-8",
    )

    prompt_template = JinjaTemplate("echo")

    agent = PatchAgent(
        context_provider=ContextProviderPreprocessor(SymbolService(tmp_path)),
        tool_provider=ToolProviderPreprocessor(),
        engine=FailingEngine(),
        model_payload={},
        prompt_template=prompt_template,
    )

    log_path = tmp_path / "err.log"
    with pytest.raises(RuntimeError):
        agent.run(
            {
                "symbol": "foo",
                "file": str(input_file),
                "experiment_id": "e",
                "run_id": "r",
                "round": 1,
                "system": "P",
                "log_path": log_path,
            }
        )
    assert log_path.exists()
