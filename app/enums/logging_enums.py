from enum import Enum
from typing import List, Optional

class LOG_TYPE(str, Enum):
    ERROR = "error_log"
    PROVIDER = "provider_log"
    STATE_TRANSITION = "state_transition_log"
    AGENT_CONVERSATION = "agent_conversation_log"
    SNAPSHOT_METRICS = "snapshot_metrics"
    FILE = "file_log"

class PROVIDER_TYPE(str, Enum):
    TOOL = "tool"
    AGENT_ENGINE = "agent_engine"
    AGENT = "agent"
    PROMPT = "prompt"
    CONTEXT = "context"
    SCORE = "score"
    STATE = "state"
    SYSTEM = "system"
    CONTROLLER = "controller"
    PROGRAM = "program"
    SESSION = "session"
    UNKNOWN = "unknown"

class ERROR_TYPE(str, Enum):
    RUNTIME = "runtime"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

class RunContext:
    def __init__(
        self,
        *,
        called_by_type: PROVIDER_TYPE,
        called_by_id: int,
        session_id: str,
        file_log_id: str,
        parent_id: Optional[str] = None,
        execution_chain: Optional[List[str]] = None,
    ):
        self.called_by_type = called_by_type
        self.called_by_id = called_by_id
        self.session_id = session_id
        self.file_log_id = file_log_id
        self.parent_id = parent_id
        self.execution_chain = execution_chain or []