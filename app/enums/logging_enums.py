from enum import Enum

class LogType(str, Enum):
    ERROR = "error"
    PROVIDER = "provider"
    STATE_TRANSITION = "state_transition"
    AGENT_CONVERSATION = "agent_conversation"
