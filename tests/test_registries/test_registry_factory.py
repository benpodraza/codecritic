import os
import sys
import types
import unittest
from pathlib import Path

from app.utils.agent_factory import build_agent
from app.registries.agent_registry import AGENT_REGISTRY
from app.registries.system_registry import SYSTEM_REGISTRY, TransitionFunction
from app.utils.symbol_graph.symbol_service import SymbolService

class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return "fake"

class DummyToolProvider:
    pass

fake_engine_module = types.SimpleNamespace(OpenAiGpt4oAgentEngineRunner=FakeEngine)
fake_jinja2 = types.SimpleNamespace(Template=lambda x: x)
fake_tp_module = types.SimpleNamespace(PreprocessingToolProvider=DummyToolProvider)

class RegistryFactoryTests(unittest.TestCase):
    def setUp(self):
        os.environ["OPENAI_API_KEY"] = "fake"
        sys.modules['app.utils.engine.openai_gpt4o_runner'] = fake_engine_module
        sys.modules['jinja2'] = fake_jinja2
        sys.modules['app.tool_providers.preprocessing_tool_provider'] = fake_tp_module
        self.symbol_service = SymbolService(Path('.'))

    def test_agent_registry_entries(self):
        self.assertIn('generator', AGENT_REGISTRY)
        entry = AGENT_REGISTRY['generator']
        self.assertEqual(entry.engine_config['temperature'], '0.3')

    def test_build_agent(self):
        agent = build_agent('generator', self.symbol_service)
        from app.agents.generator_agent import GeneratorAgent
        self.assertIsInstance(agent, GeneratorAgent)
        self.assertEqual(agent.engine.call_engine('x', {}), 'fake')

    def test_system_registry(self):
        self.assertIn('refactoring', SYSTEM_REGISTRY)
        system = SYSTEM_REGISTRY['refactoring']
        self.assertEqual(system.transition_function, TransitionFunction.DEFAULT)
        self.assertIn('generator', system.agents)

if __name__ == '__main__':
    unittest.main()
