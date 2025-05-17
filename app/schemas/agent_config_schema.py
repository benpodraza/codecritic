from typing import Dict, Optional
from openai import BaseModel

from app.schemas.shared_config_schemas import ModelEngine, PromptVariant


class AgentConfig(BaseModel):
    name: str  # e.g., "PatchAgent"
    engine: ModelEngine
    engine_config: Dict[str, Optional[str]]
    prompt_variant: PromptVariant
    base_prompt_path: str