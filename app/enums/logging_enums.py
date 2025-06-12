from enum import Enum

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