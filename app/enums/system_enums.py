from __future__ import annotations

from enum import Enum


class SystemState(Enum):
    INIT = "init"
    RUNNING = "running"
    COMPLETE = "complete"
