from __future__ import annotations

from enum import Enum


class SystemState(Enum):
    INIT = "init"
    RUNNING = "running"
    COMPLETE = "complete"


class FSMState(Enum):
    """Finite state machine states for the CodeCritic system."""

    START = "start"
    GENERATE = "generate"
    DISCRIMINATE = "discriminate"
    MEDIATE = "mediate"
    PATCHOR = "patchor"
    RECOMMENDER = "recommender"
    END = "end"
