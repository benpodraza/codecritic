from __future__ import annotations

from enum import Enum


class AGENT_TYPE(str, Enum):
    GENERATOR = "generator"
    DISCRIMINATOR = "discriminator"
    MEDIATOR = "mediator"
    STABILITY = "stability"
    BASIC = "basic"
    UNKNOWN = "unknown"

class AGENT_STATE(Enum):
    INIT = "init"
    RUNNING = "running"
    COMPLETE = "complete"
