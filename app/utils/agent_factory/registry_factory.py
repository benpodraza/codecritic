from importlib import import_module
from pathlib import Path
from typing import Any

from app.registries.agent_registry import AGENT_REGISTRY
from app.utils.symbol_graph.symbol_service import SymbolService

from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def build_agent(agent_key: str, symbol_service: SymbolService) -> Any:
    entry = AGENT_REGISTRY[agent_key]

    module_path, class_name = entry.agent_class.rsplit(".", 1)
    AgentCls = getattr(import_module(module_path), class_name)

    cp_module, cp_class = entry.context_provider_class.rsplit(".", 1)
    ContextProviderCls = getattr(import_module(cp_module), cp_class)

    tp_module, tp_class = entry.tool_provider_class.rsplit(".", 1)
    ToolProviderCls = getattr(import_module(tp_module), tp_class)

    context_provider = ContextProviderCls(symbol_service)
    tool_provider = ToolProviderCls()

    prompt_path = Path(entry.prompt_template_path).resolve()
    env = Environment(loader=FileSystemLoader(prompt_path.parent))
    prompt_template = env.get_template(prompt_path.name)

    engine_cls = entry.engine.runner_class
    if engine_cls is None:
        raise ValueError("Engine runner not defined for entry")
    engine = engine_cls()

    return AgentCls(
        context_provider=context_provider,
        tool_provider=tool_provider,
        engine=engine,
        model_payload=entry.engine_config,
        prompt_template=prompt_template,
    )
