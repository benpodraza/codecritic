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


@dataclass
class PromptLog:
    """Log entry for prompts generated and executed by agents."""

    experiment_id: str
    round: int
    system: str
    agent_id: str
    agent_role: str
    agent_engine: str | None = None
    symbol: str | None = None
    prompt: str | None = None
    response: str | None = None
    attempt_number: int = 0
    agent_action_outcome: str | None = None
    start: datetime = field(default_factory=datetime.utcnow)
    stop: datetime | None = None


@dataclass
class CodeQualityLog:
    """Log entry for static analysis and linting results."""

    experiment_id: str
    round: int
    symbol: str
    lines_of_code: int
    cyclomatic_complexity: float
    maintainability_index: float
    lint_errors: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ErrorLog:
    """Log entry for errors encountered during execution."""

    experiment_id: str
    round: int
    error_type: str
    message: str
    file_path: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScoringLog:
    """Log entry for computed evaluation metrics."""

    experiment_id: str
    round: int
    metric: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
