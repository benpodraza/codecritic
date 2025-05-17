from importlib import import_module
from pathlib import Path

from app.schemas.agent_config_schema import AgentConfig
from app.utils.agents.base_agent.base_agent import BaseAgent
from app.utils.agents.engine.agent_engine_runner import AgentEngineRunner
from app.enums.agent_management_enums import AgentRole
from app.utils.symbol_graph.symbol_service import SymbolService
from app.systems.preprocessing.utils.context_provider_preprocessor import ContextProviderPreprocessor
from app.systems.preprocessing.utils.tool_provider_preprocessor import ToolProviderPreprocessor


def build_agent(role: AgentRole, config: AgentConfig, symbol_service: SymbolService) -> BaseAgent:
    """
    Dynamically build an agent instance based on AgentRole and config.

    Resolves agent class from:
        app/agents/<role>/<role>_agent.py → <Role>Agent class

    Example:
        AgentRole.PATCHOR → app.agents.patchor.patchor_agent.PatchorAgent

    Args:
        role (AgentRole): Enum (e.g., AgentRole.PATCHOR)
        config (AgentConfig): Prompt, engine, and payload config

    Returns:
        BaseAgent: Instantiated subclass
    """
    # === Load engine ===
    engine_cls = config.engine.runner_class
    if not engine_cls:
        raise ValueError(f"Unsupported engine type: {config.engine}")
    engine: AgentEngineRunner = engine_cls()

    # === Load context provider ===
    
    context_provider = ContextProviderPreprocessor(symbol_service)
    tool_provider = ToolProviderPreprocessor()

    # === Load prompt ===
    prompt_path = Path(config.base_prompt_path)
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    prompt_template = prompt_path.read_text()

    # === Resolve agent class dynamically ===
    if role == AgentRole.PATCHOR:
        module_path = "app.utils.agents.patch_agent.patch_agent"
        class_name = "PatchAgent"
    elif role == AgentRole.RECOMMENDER:
        module_path = "app.utils.agents.recommender_agent.recommender_agent"
        class_name = "RecommenderAgent"
    else:
        module_path = f"app.systems.preprocessing.agents.{role.value}.{role.value}_agent"
        class_name = "".join(part.capitalize() for part in role.value.split("_")) + "Agent"



    try:
        agent_module = import_module(module_path)
        agent_cls = getattr(agent_module, class_name)
    except (ModuleNotFoundError, AttributeError) as e:
        raise ImportError(
            f"❌ Could not resolve agent class for role `{role}`.\n"
            f"Tried: {module_path}.{class_name}\n"
            f"Error: {e}"
        )

    return agent_cls(
        context_provider=context_provider,
        tool_provider=tool_provider,
        engine=engine,
        model_payload=config.engine_config,
        prompt_template=prompt_template
    )
