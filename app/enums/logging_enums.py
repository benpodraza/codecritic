from enum import Enum

class LogType(str, Enum):
    ERROR = "error_log"
    PROVIDER = "provider_log"
    STATE_TRANSITION = "state_transition_log"
    AGENT_CONVERSATION = "agent_conversation_log"
