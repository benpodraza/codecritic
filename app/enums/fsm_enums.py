from enum import Enum

class STATE_TYPE(str, Enum):
    START = "start"
    INTERMEDIATE = "intermediate"
    END = "end"


class DECISION_TYPE(str, Enum):
    INITIAL = "initial"
    IMPROVED = "improved"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNKNOWN = "unknown"

class TRANSITION_REASON_TYPE(str, Enum):
    INITIALIZATION = "initialization"
    SUCCESSFUL = "completed successfully"
    UNSUCCESSFUL = "completed unsuccessfully"
    GENERATING = "generating"
    EVALUATING = "evaluating" 
    ERROR = "error"
    CUSTOM_RULE = "custom_rule"

