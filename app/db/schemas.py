from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from app.utilities.pydantic_compat import field_validator

class AgentPromptSchema(BaseModel):
    id: Optional[int]
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str]
    artifact_path: Path
    tags: Optional[List[str]] = None

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class SystemPromptSchema(BaseModel):
    id: Optional[int]
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str]
    artifact_path: Path
    tags: Optional[List[str]] = None

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class ToolConfig(BaseModel):
    """Configuration for an agent tool."""

    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict] = None
    artifact_path: Path

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

