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
        agent_class="app.agents.generator_agent.GeneratorAgent",
        context_provider_class="app.context_providers.preprocessing_provider.PreprocessingContextProvider",
        tool_provider_class="app.tool_providers.preprocessing_tool_provider.PreprocessingToolProvider",
        prompt_template_path="app/prompts/generator_prompt.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "discriminator": AgentEntry(
        agent_class="app.agents.discriminator_agent.DiscriminatorAgent",
        context_provider_class="app.context_providers.preprocessing_provider.PreprocessingContextProvider",
        tool_provider_class="app.tool_providers.preprocessing_tool_provider.PreprocessingToolProvider",
        prompt_template_path="app/prompts/discriminator_prompt.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "mediator": AgentEntry(
        agent_class="app.agents.mediator_agent.MediatorAgent",
        context_provider_class="app.context_providers.preprocessing_provider.PreprocessingContextProvider",
        tool_provider_class="app.tool_providers.preprocessing_tool_provider.PreprocessingToolProvider",
        prompt_template_path="app/prompts/mediator_prompt.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "patchor": AgentEntry(
        agent_class="app.agents.patch_agent.PatchAgent",
        context_provider_class="app.context_providers.preprocessing_provider.PreprocessingContextProvider",
        tool_provider_class="app.tool_providers.preprocessing_tool_provider.PreprocessingToolProvider",
        prompt_template_path="app/utils/patch_agent/patch_agent.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
    "recommender": AgentEntry(
        agent_class="app.agents.recommender_agent.RecommenderAgent",
        context_provider_class="app.context_providers.preprocessing_provider.PreprocessingContextProvider",
        tool_provider_class="app.tool_providers.preprocessing_tool_provider.PreprocessingToolProvider",
        prompt_template_path="app/utils/recommender_agent/recommender_agent.txt",
        engine=ModelEngine.GPT_4O,
        engine_config={"temperature": "0.3"},
        prompt_variant=PromptVariant.ZERO_SHOT,
    ),
}
