from __future__ import annotations

from enum import Enum


class AGENT(str, Enum):
    START = "start"
    END = "end"
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
