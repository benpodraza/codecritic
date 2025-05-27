from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, JSON
from sqlalchemy.dialects.sqlite import TEXT
from app.db.base import Base
from uuid import uuid4

from app.enums.system_enums import SystemType

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
    system_type = Column(Enum(SystemType), nullable=False) 
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
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)


class AgentProviderConfig(Base):
    __tablename__ = "agent_provider_config" 

    id = Column(Integer, primary_key=True)
    guid = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
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

class OrchestratorProviderConfig(Base):
    __tablename__ = "orchestrator_provider_config"

    id = Column(Integer, primary_key=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
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
    session_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    environment_type = Column(String, nullable=False)  # e.g., "experiment", "live", "staging"
    config = Column(JSON, nullable=True)
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
    snapshot_id = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    transition_from = Column(String, nullable=True)
    transition_to = Column(String, nullable=True)
    
class StateTransitionLog(Base):
    __tablename__ = "state_transition_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    from_state = Column(String, nullable=False)
    to_state = Column(String, nullable=False)
    input_snapshot_id = Column(String, nullable=True)
    output_snapshot_id = Column(String, nullable=True)

class AgentConversationLog(Base):
    __tablename__ = "agent_conversation_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    system = Column(String, nullable=False)
    agent_provider_config_id = Column(Integer, nullable=False)  
    agent_name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

class ErrorLog(Base):
    __tablename__ = "error_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    provider_id = Column(Integer, nullable=True)
    provider_type = Column(String, nullable=True)
    error_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    file_path = Column(String, nullable=True)