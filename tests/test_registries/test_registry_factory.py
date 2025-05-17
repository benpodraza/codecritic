import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Set BEFORE imports
os.environ["OPENAI_API_KEY"] = "fake-key"

from app.utils.agents.agent_factory.registry_factory import build_agent
from app.registries.agent_registry import AGENT_REGISTRY
from app.registries.system_registry import SYSTEM_REGISTRY, TransitionFunction
from app.utils.symbol_graph.symbol_service import SymbolService


# Properly mocked engine class
class FakeEngine:
    def call_engine(self, prompt: str, config: dict) -> str:
        return "fake"


class DummyToolProvider:
    pass


fake_engine_module = types.SimpleNamespace(OpenAiGpt4oAgentEngineRunner=FakeEngine)
fake_tp_module = types.SimpleNamespace(PreprocessingToolProvider=DummyToolProvider)

# Test class
class RegistryFactoryTests(unittest.TestCase):
    def setUp(self):
        # Backup original modules
        self.orig_engine = sys.modules.get('app.utils.agents.engine.openai_gpt4o_runner')
        self.orig_jinja2 = sys.modules.get('jinja2')
        self.orig_tp = sys.modules.get('app.tool_providers.preprocessing_tool_provider')

        # Mock the modules in sys.modules directly
        sys.modules['app.utils.agents.engine.openai_gpt4o_runner'] = fake_engine_module
        sys.modules['app.tool_providers.preprocessing_tool_provider'] = fake_tp_module

        # Mock Jinja2 Environment and Template properly
        mock_template = MagicMock()
        mock_template.render.return_value = "fake-prompt"
        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template

        self.jinja_patcher = patch('app.utils.agents.agent_factory.registry_factory.Environment', return_value=mock_env)
        self.jinja_patcher.start()

        # Symbol service setup
        self.symbol_service = SymbolService(Path('.'))

    def tearDown(self):
        # Restore original modules
        if self.orig_engine is not None:
            sys.modules['app.utils.agents.engine.openai_gpt4o_runner'] = self.orig_engine
        else:
            del sys.modules['app.utils.agents.engine.openai_gpt4o_runner']

        if self.orig_jinja2 is not None:
            sys.modules['jinja2'] = self.orig_jinja2
        else:
            sys.modules.pop('jinja2', None)

        if self.orig_tp is not None:
            sys.modules['app.tool_providers.preprocessing_tool_provider'] = self.orig_tp
        else:
            del sys.modules['app.tool_providers.preprocessing_tool_provider']

        # Stop patching
        self.jinja_patcher.stop()

    def test_agent_registry_entries(self):
        self.assertIn('generator', AGENT_REGISTRY)
        entry = AGENT_REGISTRY['generator']
        self.assertEqual(entry.engine_config['temperature'], '0.3')

    def test_build_agent(self):
        agent = build_agent('generator', self.symbol_service)
        from app.agents.generator_agent import GeneratorAgent
        self.assertIsInstance(agent, GeneratorAgent)
        # Explicitly test mocked response
        self.assertEqual(agent.engine.call_engine('x', {}), 'fake')
        self.assertEqual(agent.prompt_template.render(), 'fake-prompt')

    def test_system_registry(self):
        self.assertIn('refactoring', SYSTEM_REGISTRY)
        system = SYSTEM_REGISTRY['refactoring']
        self.assertEqual(system.transition_function, TransitionFunction.DEFAULT)
        self.assertIn('generator', system.agents)


if __name__ == '__main__':
    unittest.main()
