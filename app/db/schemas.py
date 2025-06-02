from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator
from app.enums.agent_enums import AGENT_TYPE
from app.enums.fsm_enums import DECISION_TYPE, REASON_TYPE, STATE_TYPE, TRANSITION_REASON_TYPE
from app.enums.logging_enums import ERROR_TYPE, PROVIDER_TYPE
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.enums.system_enums import STATE_DECISION_TYPE, SYSTEM_TYPE
from app.enums.agent_engine_enums import AGENT_ENGINE_MODEL


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
    system_type: SYSTEM_TYPE
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
    name: SCORING_METRIC_TYPE = Field(..., description="The type of scoring metric used")
    value: float = Field(..., description="Final weighted score (normalized 0.0–1.0 scale)")
    components: Dict[str, float] = Field(..., description="Tool/component-specific scores")
    summary: Optional[str] = None


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
    model: AGENT_ENGINE_MODEL  # ✅ Enum enforced
    config: Optional[Dict[str, Any]] = None
    cost_per_1k_tokens: Optional[float] = Field(default=0.0)
    artifact_path: Path
    tags: Optional[List[str]] = None

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
    agent_type: AGENT_TYPE = AGENT_TYPE.UNKNOWN 

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
    provider_type: PROVIDER_TYPE
    input: Optional[str] = None
    output: Optional[str] = None
    output_schema: Optional[str] = None
    latency_ms: Optional[int] = None
    config_hash: Optional[str] = None
    file_path: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class StateTransitionLogSchema:
    session_id: str
    entity_type: PROVIDER_TYPE  # e.g., "StateProvider", "SystemProvider", etc.
    entity_id: int
    from_state: str
    to_state: str
    reason: TRANSITION_REASON_TYPE
    decision: DECISION_TYPE = DECISION_TYPE.UNKNOWN
    triggered_by: str | None = None
    step: int | None = None
    transition_metadata: dict | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AgentConversationLogSchema:
    session_id: str
    system: SYSTEM_TYPE
    agent_type: AGENT_TYPE
    agent_provider_config_id: int
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ErrorLogSchema:
    session_id: str
    error_type: ERROR_TYPE
    message: str
    file_path: str | None = None
    provider_id: int | None = None
    provider_type: PROVIDER_TYPE = PROVIDER_TYPE.UNKNOWN
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
@dataclass
class SnapshotMetricsSchema:
    session_id: str
    snapshot_id: str
    system: SYSTEM_TYPE
    agent: str
    agent_type: AGENT_TYPE 
    agent_id: int
    score: float
    state: str  # could be FSM state, usually freeform like "generate" or "stability"
    decision: DECISION_TYPE
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

# Provider output schemas (for logs)

class ToolOutputSchema(BaseModel):
    return_code: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    violations: Optional[list[str]] = None  # for linters like ruff
    metrics: Optional[Dict[str, Any]] = None  # for tools like sonarcloud
    summary: Optional[str] = None  # optional human-readable summary

class AgentEngineOutput(BaseModel):
    response: str
    token_count: int
    cost_usd: float
    snapshot_id: Optional[str] = None
    summary: Optional[str] = None

# app/db/schemas.py
class AgentOutputSchema(BaseModel):
    response: str
    log: Optional[str] = None
    decision: Optional[str] = None
    snapshot_id: Optional[str] = None

class ContextOutputSchema(BaseModel):
    context: dict
    summary: Optional[str] = None

class PromptOutputSchema(BaseModel):
    prompt: str
    summary: Optional[str] = None

class FSMOutputSchema(BaseModel):
    state: str
    previous_state: Optional[str] = None
    state_type: STATE_TYPE = STATE_TYPE.INTERMEDIATE
    reason: REASON_TYPE = REASON_TYPE.UNSPECIFIED
    decision: Optional[STATE_DECISION_TYPE] = STATE_DECISION_TYPE.UNKNOWN
    steps: int = Field(..., ge=0)
    max_steps: int = Field(..., gt=0)
    summary: Optional[str] = None
    output: Optional[dict] = None
    provider_name: Optional[str] = None

class StateOutputSchema(FSMOutputSchema): pass
class SystemOutputSchema(FSMOutputSchema): pass
class ControllerOutputSchema(FSMOutputSchema): pass
class ProgramOutputSchema(FSMOutputSchema): pass


# DTOs

class Snapshot(BaseModel):
    timestamp: datetime
    file: str
    score: float
    decision: DECISION_TYPE

class SystemState(BaseModel):
    system: str
    file_path: str
    working_file: str
    final_file: Optional[str] = None
    snapshots: List[Snapshot]
    state: Optional[str] = "active"


