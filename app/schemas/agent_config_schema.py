from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import field_validator, model_validator

from .agent_engine_schema import AgentEngine
from .prompt_generator_schema import PromptGenerator


class AgentConfig(BaseModel):
    """Schema for the agent_config table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    agent_role: Optional[str] = None
    system_type: Optional[str] = None
    agent_engine_id: Optional[int] = None
    prompt_generator_id: Optional[int] = None
    agent_engine: Optional[AgentEngine] = None
    prompt_generator: Optional[PromptGenerator] = None
    artifact_path: Optional[Path] = None

    table_name: str = "agent_config"

    @model_validator(mode="after")
    def _sync_ids(self) -> "AgentConfig":
        if self.agent_engine is not None and self.agent_engine_id is None:
            self.agent_engine_id = getattr(self.agent_engine, "id", None)
        if self.prompt_generator is not None and self.prompt_generator_id is None:
            self.prompt_generator_id = getattr(self.prompt_generator, "id", None)
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
