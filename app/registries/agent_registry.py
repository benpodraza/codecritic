from pydantic import BaseModel
from typing import Dict, Optional

from app.schemas.shared_config_schemas import ModelEngine, PromptVariant

class AgentEntry(BaseModel):
    agent_class: str
    context_provider_class: str
    tool_provider_class: str
    prompt_template_path: str
    engine: ModelEngine
    engine_config: Dict[str, Optional[str]]
    prompt_variant: PromptVariant

AGENT_REGISTRY = {
    "generator": AgentEntry(
        agent_class="app.systems.preprocessing.agents.generator.generator_agent.GeneratorAgent",
        context_provider_class="app.systems.preprocessing.utils.context_provider_preprocessor.ContextProviderPreprocessor",
        tool_provider_class="app.systems.preprocessing.utils.tool_provider_preprocessor.ToolProviderPreprocessor",
        prompt_template_path="app/systems/preprocessing/agents/generator/prompts/zero_shot.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "discriminator": AgentEntry(
        agent_class="app.systems.preprocessing.agents.discriminator.discriminator_agent.DiscriminatorAgent",
        context_provider_class="app.systems.preprocessing.utils.context_provider_preprocessor.ContextProviderPreprocessor",
        tool_provider_class="app.systems.preprocessing.utils.tool_provider_preprocessor.ToolProviderPreprocessor",
        prompt_template_path="app/systems/preprocessing/agents/discriminator/prompts/discriminator.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "mediator": AgentEntry(
        agent_class="app.systems.preprocessing.agents.mediator.mediator_agent.MediatorAgent",
        context_provider_class="app.systems.preprocessing.utils.context_provider_preprocessor.ContextProviderPreprocessor",
        tool_provider_class="app.systems.preprocessing.utils.tool_provider_preprocessor.ToolProviderPreprocessor",
        prompt_template_path="app/systems/preprocessing/agents/mediator/prompts/mediator.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "patchor": AgentEntry(
        agent_class="app.utils.patch_agent.patch_agent.PatchAgent",
        context_provider_class="app.systems.preprocessing.utils.context_provider_preprocessor.ContextProviderPreprocessor",
        tool_provider_class="app.systems.preprocessing.utils.tool_provider_preprocessor.ToolProviderPreprocessor",
        prompt_template_path="app/utils/patch_agent/patch_agent.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "recommender": AgentEntry(
        agent_class="app.utils.recommender_agent.recommender_agent.RecommenderAgent",
        context_provider_class="app.systems.preprocessing.utils.context_provider_preprocessor.ContextProviderPreprocessor",
        tool_provider_class="app.systems.preprocessing.utils.tool_provider_preprocessor.ToolProviderPreprocessor",
        prompt_template_path="app/utils/recommender_agent/recommender_agent.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
}
