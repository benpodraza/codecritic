from importlib import import_module
from app.schemas.experiment_config_schemas import EvaluatorConfig
from app.utils.agents.base_agent.tool_provider import ToolProvider
from app.utils.experiments.evaluation.system_evaluator import SystemEvaluator

def build_evaluator(config: EvaluatorConfig, tool_provider: ToolProvider) -> SystemEvaluator:
    module_path = f"app.utils.evaluation.{config.name}.{config.name}_{config.version}"
    class_name = "".join(part.capitalize() for part in config.name.split("_"))

    mod = import_module(module_path)
    cls = getattr(mod, class_name)
    return cls(tool_provider=tool_provider)
