from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, DateTime, Enum, Float, Integer, String, JSON
from sqlalchemy.dialects.sqlite import TEXT
from app.db.base import Base
from uuid import uuid4

from app.enums.agent_enums import AGENT_TYPE
from app.enums.system_enums import SYSTEM_TYPE
from sqlalchemy.orm import Mapped, mapped_column

## PROMPT CONFIGS

class AgentPrompt(Base):
    __tablename__ = 'agent_prompt'
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class SystemPrompt(Base):
    __tablename__ = 'system_prompt'
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    system_type = Column(Enum(SYSTEM_TYPE), nullable=False) 
    description = Column(String)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)


## PROVIDER CONFGIS

class PromptProviderConfig(Base):
    __tablename__ = "prompt_provider_config"

    id = Column(Integer, primary_key=True, index=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    artifact_path = Column(String, nullable=False)
    config = Column(JSON, nullable=False) 
    tags = Column(JSON, nullable=True)

class ToolProviderConfig(Base):
    __tablename__ = "tool_provider_config"
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class ScoreProviderConfig(Base):
    __tablename__ = "score_provider_config" 
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class ContextProviderConfig(Base):
    __tablename__ = "context_provider_config" 
    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class AgentEngineProviderConfig(Base):
    __tablename__ = "agent_engine_provider_config" 

    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    model= Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    cost_per_1k_tokens = Column(Float, nullable=True, default=0.0)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)


class AgentProviderConfig(Base):
    __tablename__ = "agent_provider_config" 

    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    agent_type = Column(String, nullable=False, default="unknown")
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class StateProviderConfig(Base):
    __tablename__ = "state_provider_config"

    id = Column(Integer, primary_key=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class SystemProviderConfig(Base):
    __tablename__ = "system_provider_config"

    id = Column(Integer, primary_key=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class ControllerProviderConfig(Base):
    __tablename__ = "controller_provider_config"

    id = Column(Integer, primary_key=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)        # expects {"systems": {"name": id, …}, …}
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)


class ProgramProviderConfig(Base):
    __tablename__ = "program_provider_config"

    id = Column(Integer, primary_key=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)

class SessionConfig(Base):
    __tablename__ = "session_config"

    id = Column(Integer, primary_key=True)
    program_provider_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    environment_type = Column(String, nullable=False)  # e.g., "experiment", "live", "staging"
    tags = Column(JSON, nullable=True)


## LOGS

class ProviderLog(Base):
    __tablename__ = "provider_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    provider_id = Column(Integer, nullable=False)
    provider_type = Column(String, nullable=False)
    input = Column(String, nullable=True)
    output = Column(String, nullable=True)
    output_schema = Column(String, nullable=True) 
    latency_ms = Column(Integer, nullable=True)   
    config_hash = Column(String, nullable=True)   
    file_name = Column(String, nullable=True)
    called_by_type = Column(String, nullable=True)
    called_by_id = Column(Integer, nullable=True)
    run_id = Column(TEXT, nullable=False, index=True)

    
class StateTransitionLog(Base):
    __tablename__ = "state_transition_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    from_state = Column(String, nullable=False)
    to_state = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    decision = Column(String, nullable=True)    
    triggered_by = Column(String, nullable=True)   
    step = Column(Integer, nullable=True)   
    transition_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    input_snapshot_id = Column(String, nullable=True)
    output_snapshot_id = Column(String, nullable=True)
    run_id = Column(TEXT, nullable=False, index=True)

class AgentConversationLog(Base):
    __tablename__ = "agent_conversation_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    system = Column(String, nullable=False)
    agent_provider_config_id = Column(Integer, nullable=False)
    agent_type = Column(String, nullable=False)  # NEW: replaces `agent_name`
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    run_id = Column(TEXT, nullable=False, index=True)

class ErrorLog(Base):
    __tablename__ = "error_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    latency_ms = Column(Integer, nullable=True) 
    provider_id = Column(Integer, nullable=True)
    provider_type = Column(String, nullable=True)
    error_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    called_by_type = Column(String, nullable=True)
    called_by_id = Column(Integer, nullable=True)
    run_id = Column(TEXT, nullable=False, index=True)

class SnapshotMetrics(Base):
    __tablename__ = "snapshot_metrics"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False)
    snapshot_id = Column(String, nullable=False)
    system = Column(String, nullable=True)
    agent = Column(String, nullable=True)
    agent_type = Column(Enum(AGENT_TYPE), nullable=True)
    agent_id = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)
    state = Column(String, nullable=True)
    decision = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    # structural metrics
    line_count_before = Column(Integer)
    line_count_after = Column(Integer)
    function_count_before = Column(Integer)
    function_count_after = Column(Integer)
    symbol_count_before = Column(Integer)
    symbol_count_after = Column(Integer)
    branch_count_before = Column(Integer)
    branch_count_after = Column(Integer)
    comment_count_before = Column(Integer)
    comment_count_after = Column(Integer)

    # deltas
    line_count_delta = Column(Integer)
    function_count_delta = Column(Integer)
    symbol_count_delta = Column(Integer)
    branch_count_delta = Column(Integer)
    comment_count_delta = Column(Integer)


