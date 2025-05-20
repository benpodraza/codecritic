from __future__ import annotations

from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from app.enums.system_enums import SystemType
from app.utilities.pydantic_compat import field_validator


class AgentPrompt(BaseModel):
    """Schema for the agent_prompt table."""

    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    agent_role: str
    system_type: SystemType
    artifact_path: Path
    
    table_name: str = "agent_prompt"

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
        return super().model_dump(**kwargs)
