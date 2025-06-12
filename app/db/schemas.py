from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator

from app.enums.fsm_enums import DECISION_TYPE, STATE_TYPE, TRANSITION_REASON_TYPE
from app.enums.logging_enums import ERROR_TYPE, PROVIDER_TYPE
from app.enums.scoring_enums import SCORING_METRIC_TYPE
from app.enums.controller_enums import CONTROLLER
from app.enums.system_enums import SYSTEM
from app.enums.state_enums import STATE
from app.enums.agent_enums import AGENT
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
    system_type: SYSTEM
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
    agent_type: AGENT = AGENT.UNKNOWN 

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
    system_type: SYSTEM

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
    file_name: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    called_by_type: Optional[PROVIDER_TYPE] = None
    called_by_id: Optional[int] = None
    run_id: str = field(default_factory=lambda: str(uuid4()))
    file_log_id: Optional[str] = None

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
    run_id: str = field(default_factory=lambda: str(uuid4()))
    called_by_type: PROVIDER_TYPE | None = None
    called_by_id: int | None = None 
    file_log_id: Optional[str] = None

@dataclass
class AgentConversationLogSchema:
    session_id: str
    system: SYSTEM
    agent_type: AGENT
    agent_provider_config_id: int
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: str = field(default_factory=lambda: str(uuid4()))
    file_log_id: Optional[str] = None

@dataclass
class ErrorLogSchema:
    session_id: str
    error_type: ERROR_TYPE
    message: str
    file_path: str | None = None
    provider_id: int | None = None
    provider_type: PROVIDER_TYPE = PROVIDER_TYPE.UNKNOWN
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: Optional[int] = None
    called_by_type: Optional[PROVIDER_TYPE] = None
    called_by_id: Optional[int] = None
    run_id: str = field(default_factory=lambda: str(uuid4()))
    file_log_id: Optional[str] = None
    
@dataclass
class SnapshotMetricsSchema:
    session_id: str
    snapshot_id: str
    system: SYSTEM
    agent: str
    agent_type: AGENT 
    agent_id: int
    score: float
    state: str  # could be FSM state, usually freeform like "generate" or "stability"
    decision: DECISION_TYPE
    timestamp: datetime
    file_log_id: str

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
class FileLogSchema:
    session_id: str
    file_name: str
    id: Optional[int] = None
    original_path: Optional[str] = None
    length_bytes: Optional[int] = None


# Provider output schemas (for logs)

class ToolOutputSchema(BaseModel):
    return_code: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    violations: Optional[List[str]] = None  # for linters like ruff
    metrics: Optional[Dict[str, Any]] = None  # for tools like sonarcloud
    summary: Optional[str] = None  # optional human-readable summary


class AgentEngineOutput(BaseModel):
    response: str
    token_count: int
    cost_usd: float
    snapshot_id: Optional[str] = None
    summary: Optional[str] = None
    code: Optional[str] = None 
    agent_decision: Optional[str] = None
    conversation_log_entry: Optional[str] = None


class AgentOutputSchema(BaseModel):
    decision: DECISION_TYPE = DECISION_TYPE.UNKNOWN
    score: Optional[float] = None
    response: Optional[str] = None
    log: Optional[str] = None
    file_path: Optional[str] = None


class ContextOutputSchema(BaseModel):
    context: Dict[str, Any]
    summary: Optional[str] = None


class PromptOutputSchema(BaseModel):
    prompt: str
    summary: Optional[str] = None


class FSMOutputSchema(BaseModel):
    state: STATE
    previous_state: Optional[STATE] = None
    state_type: STATE_TYPE = STATE_TYPE.INTERMEDIATE
    decision: Optional[DECISION_TYPE] = DECISION_TYPE.UNKNOWN
    steps: int = Field(..., ge=0)
    max_steps: int = Field(..., gt=0)
    summary: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    provider_name: Optional[str] = None

class SystemOutputSchema(FSMOutputSchema): pass

class StateOutputSchema(FSMOutputSchema): 
    previous_state: Optional[AGENT] = None
class ProgramOutputSchema(FSMOutputSchema):
    previous_state: Optional[CONTROLLER] = None
class ControllerOutputSchema(FSMOutputSchema): 
    previous_state: Optional[SYSTEM] = None


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


