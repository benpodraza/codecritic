import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from app.utils.patch_agent import patch_agent as patch_module
from app.utils.symbol_graph.symbol_service import SymbolService

# Replace loggers inside the patch_agent module
patch_module.PromptLogger = lambda *_args, **_kwargs: SimpleNamespace(log=lambda **k: None)
patch_module.ConversationLogger = lambda *_args, **_kwargs: SimpleNamespace(log=lambda **k: None)
patch_module.ErrorLogger = lambda *_args, **_kwargs: SimpleNamespace(log=lambda **k: None)

PatchAgent = patch_module.PatchAgent

# Provide dummy loggers to avoid file writes

class DummyContextProvider:
    def get_context(self, inputs):
        return {"code": "print('hi')"}

class DummyEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return "print('patched')\n# === AI-FIRST METADATA ===\n# key: val"

class PatchAgentRunTest(unittest.TestCase):
    def test_run_returns_response(self):
        os.environ['OPENAI_API_KEY'] = 'fake'
        with tempfile.TemporaryDirectory() as tmpdir:
            symbol_service = SymbolService(Path(tmpdir))
            agent = PatchAgent(
                context_provider=DummyContextProvider(),
                tool_provider=None,
                engine=DummyEngine(),
                model_payload={},
                prompt_template="{code}"
            )

            result = agent.run({
                "symbol": "foo",
                "file": str(Path(tmpdir)/"test.py"),
                "experiment_id": "e1",
                "run_id": "r1",
                "round": 1,
                "system": "demo",
                "log_path": Path(tmpdir)
            })

            self.assertIn("response", result)
            self.assertIn("prompt", result)
            self.assertIn("patched", result["response"])

if __name__ == '__main__':
    unittest.main()
