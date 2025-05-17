from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StateLog:
    experiment_id: str
    system: str
    round: int
    state: str
    action: str
    score: float | None = None
    details: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StateTransitionLog:
    experiment_id: str
    round: int
    from_state: str
    to_state: str
    reason: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
