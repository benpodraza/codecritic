from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
from app.enums.agent_enums import AgentRole
from app.enums.system_enums import Decision, SystemType


class AgentPromptSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    artifact_path: Path
    tags: Optional[List[str]] = None

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class SystemPromptSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    system_type: SystemType
    description: Optional[str] = None
    artifact_path: Path
    tags: Optional[List[str]] = None

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class PromptProviderConfig(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    artifact_path: Path
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = Field(default_factory=list)

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class ToolProviderConfig(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    artifact_path: Path
    tags: Optional[List[str]] = None

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class ScoreOutputSchema(BaseModel):
    name: str = Field(..., description="The name of the scoring metric (e.g., 'linting_score').")
    value: float = Field(..., description="The final weighted score, normalized to a 0.0–1.0 scale.")
    components: Dict[str, float] = Field(
        ...,
        description="Component scores used to compute the overall score. Keys should match tool names."
    )

class ScoreProviderConfig(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    artifact_path: Optional[Path] = None
    tags: Optional[List[str]] = None
    table_name: str = "score_provider"

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Optional[Path]) -> Optional[Path]:
        if v is None:
            return v
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v
        
class AgentEngineProviderConfig(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    model: str
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    artifact_path: Path

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class AgentProviderConfigSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    artifact_path: Path
    tags: Optional[list[str]] = None

    @field_validator("artifact_path")
    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class StateProviderConfigSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    artifact_path: Path
    tags: Optional[list[str]] = None

    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class SystemProviderConfigSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    artifact_path: Path
    tags: Optional[list[str]] = None

    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class ControllerProviderConfigSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    artifact_path: Path
    tags: Optional[list[str]] = None

    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class ProgramProviderConfigSchema(BaseModel):
    id: Optional[int] = None
    guid: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    artifact_path: Path
    tags: Optional[List[str]] = None

    @classmethod
    def validate_artifact_path(cls, v: Path) -> Path:
        if not v.is_absolute() and ".." in v.parts:
            raise ValueError("Invalid artifact path")
        return v

class SessionConfigSchema(BaseModel):
    id: Optional[int] = None
    session_id: str
    name: str
    description: Optional[str] = None
    environment_type: str  # e.g., "experiment", "live", "staging"
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    

# LOGS

@dataclass
class ProviderLogSchema:
    session_id: str
    provider_id: int
    provider_type: str
    input: Optional[str] = None
    output: Optional[str] = None
    snapshot_id: Optional[str] = None
    file_path: Optional[str] = None
    transition_from: Optional[str] = None
    transition_to: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class StateTransitionLogSchema:
    session_id: str
    entity_type: str
    entity_id: int
    from_state: str
    to_state: str
    reason: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AgentConversationLogSchema:
    session_id: str
    system: str
    agent_provider_config_id: int
    agent_name: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class SnapshotMetricsSchema:
    session_id: str
    snapshot_id: str
    system: str
    agent: str
    score: float
    state: str
    decision: str
    timestamp: datetime

    line_count_before: int
    line_count_after: int
    function_count_before: int
    function_count_after: int
    symbol_count_before: int
    symbol_count_after: int
    branch_count_before: int
    branch_count_after: int
    comment_count_before: int
    comment_count_after: int

    line_count_delta: int
    function_count_delta: int
    symbol_count_delta: int
    branch_count_delta: int
    comment_count_delta: int


@dataclass
class ErrorLogSchema:
    session_id: str             
    error_type: str                   
    message: str                    
    file_path: str | None = None       
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# DTOs

class Snapshot(BaseModel):
    timestamp: datetime
    file: str
    score: float
    decision: Decision

class SystemState(BaseModel):
    system: str
    file_path: str
    working_file: str
    final_file: Optional[str] = None
    snapshots: List[Snapshot]
    state: Optional[str] = "active"