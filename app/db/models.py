from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, JSON
from sqlalchemy.dialects.sqlite import TEXT
from app.db.base import Base
from uuid import uuid4

class AgentPrompt(Base):
    __tablename__ = 'agent_prompt'
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)  # JSON column for tags explicitly

class SystemPrompt(Base):
    __tablename__ = 'system_prompt'
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    artifact_path = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)  # JSON column for tags explicitly

class ToolConfig(Base):
    __tablename__ = 'tool_config'

    id = Column(Integer, primary_key=True, index=True)
    guid = Column(TEXT, unique=True, default=lambda: str(uuid4()), nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=True)
    artifact_path = Column(String, nullable=False)

class ToolInvocationLog(Base):
    __tablename__ = "tool_invocation_log"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String, nullable=False)
    round = Column(Integer, nullable=False)
    tool_provider_name = Column(String, nullable=False)
    tool_provider_guid = Column(String, nullable=False)  # ✅ ADD THIS COLUMN
    invocation_parameters = Column(String, nullable=False)
    stdout = Column(String, nullable=True)
    stderr = Column(String, nullable=True)
    return_code = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
