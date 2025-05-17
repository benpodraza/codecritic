import os
import sys
import types
import unittest
from pathlib import Path

from app.utils.agent_factory import build_agent
from app.registries.agent_registry import AGENT_REGISTRY
from app.utils.symbol_graph.symbol_service import SymbolService
from app.schemas.shared_config_schemas import PromptVariant

class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return "fake"

class DummyToolProvider:
    pass

fake_engine_module = types.SimpleNamespace(OpenAiGpt4oAgentEngineRunner=FakeEngine)
fake_jinja2 = types.SimpleNamespace(Template=lambda x: x)
fake_tp_module = types.SimpleNamespace(PreprocessingToolProvider=DummyToolProvider)

class BuildAgentTests(unittest.TestCase):
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = "fake"
        self.orig_engine = sys.modules.get('app.utils.engine.openai_gpt4o_runner')
        self.orig_jinja2 = sys.modules.get('jinja2')
        self.orig_tp = sys.modules.get('app.tool_providers.preprocessing_tool_provider')
        sys.modules['app.utils.engine.openai_gpt4o_runner'] = fake_engine_module
        sys.modules['jinja2'] = fake_jinja2
        sys.modules['app.tool_providers.preprocessing_tool_provider'] = fake_tp_module
        self.symbol_service = SymbolService(Path('.'))

    def tearDown(self):
        if self.orig_engine is not None:
            sys.modules['app.utils.engine.openai_gpt4o_runner'] = self.orig_engine
        else:
            del sys.modules['app.utils.engine.openai_gpt4o_runner']
        if self.orig_jinja2 is not None:
            sys.modules['jinja2'] = self.orig_jinja2
        else:
            del sys.modules['jinja2']
        if self.orig_tp is not None:
            sys.modules['app.tool_providers.preprocessing_tool_provider'] = self.orig_tp
        else:
            del sys.modules['app.tool_providers.preprocessing_tool_provider']
        if 'bad' in AGENT_REGISTRY:
            del AGENT_REGISTRY['bad']

    def test_build_agent_success(self):
        agent = build_agent('generator', self.symbol_service)
        from app.agents.generator_agent import GeneratorAgent
        self.assertIsInstance(agent, GeneratorAgent)
        self.assertEqual(agent.engine.call_engine('x', {}), 'fake')

    def test_build_agent_missing_engine(self):
        # create copy of existing entry and remove engine runner
        entry = AGENT_REGISTRY['generator'].copy()
        entry.engine = types.SimpleNamespace(runner_class=None)
        AGENT_REGISTRY['bad'] = entry
        with self.assertRaises(ValueError):
            build_agent('bad', self.symbol_service)

if __name__ == '__main__':
    unittest.main()
