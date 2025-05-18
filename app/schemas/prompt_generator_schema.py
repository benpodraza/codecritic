from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import field_validator, model_validator

from .agent_prompt_schema import AgentPrompt
from .system_prompt_schema import SystemPrompt
from .context_provider_schema import ContextProvider


class PromptGenerator(BaseModel):
    """Schema for the prompt_generator table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    agent_prompt_id: Optional[int] = None
    system_prompt_id: Optional[int] = None
    content_provider_id: Optional[int] = None

    agent_prompt: Optional[AgentPrompt] = None
    system_prompt: Optional[SystemPrompt] = None
    content_provider: Optional[ContextProvider] = None
    artifact_path: Optional[Path] = None

    table_name: str = "prompt_generator"

    @model_validator(mode="after")
    def _sync_ids(self) -> "PromptGenerator":
        if self.agent_prompt is not None and self.agent_prompt_id is None:
            self.agent_prompt_id = getattr(self.agent_prompt, "id", None)
        if self.system_prompt is not None and self.system_prompt_id is None:
            self.system_prompt_id = getattr(self.system_prompt, "id", None)
        if self.content_provider is not None and self.content_provider_id is None:
            self.content_provider_id = getattr(self.content_provider, "id", None)
        return self

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Optional[Path]) -> Optional[Path]:
        if v is None:
            return v
        p = Path(v)
        if not p.is_absolute() and ".." in p.parts:
            raise ValueError("artifact_path must be absolute or project relative")
        return p

    def model_dump(self, **kwargs) -> dict:
        return BaseModel.dict(self, **kwargs)
