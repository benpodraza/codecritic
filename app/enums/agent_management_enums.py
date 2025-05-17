# === Runtime Agent State ===
from enum import Enum, auto


class AgentState(Enum):
    IDLE = auto()
    RUNNING = auto()
    WAITING_FOR_RESULT = auto()
    COMPLETED = auto()
    FAILED = auto()


class AgentRole(str, Enum):
    GENERATOR = "generator"
    DISCRIMINATOR = "discriminator"
    MEDIATOR = "mediator"
    PATCHOR = "patchor"
    RECOMMENDER = "recommender"