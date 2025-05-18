from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from app.enums.agent_enums import AgentRole
from app.enums.system_enums import SystemState, StateTransitionReason, SystemType
from app.enums.log_enums import LogType, ScoringMetric


@dataclass
class StateLog:
    experiment_id: str
    system: str
    round: int
    state: SystemState
    action: str
    score: float | None = None
    details: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StateTransitionLog:
    experiment_id: str
    round: int
    from_state: SystemState
    to_state: SystemState
    reason: StateTransitionReason
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PromptLog:
    experiment_id: str
    round: int
    system: str
    agent_id: str
    agent_role: AgentRole
    agent_engine: str | None = None
    symbol: str | None = None
    prompt: str | None = None
    response: str | None = None
    attempt_number: int = 0
    agent_action_outcome: str | None = None
    start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stop: datetime | None = None


@dataclass
class CodeQualityLog:
    experiment_id: str
    round: int
    symbol: str
    lines_of_code: int
    cyclomatic_complexity: float
    maintainability_index: float
    lint_errors: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ErrorLog:
    experiment_id: str
    round: int
    error_type: str
    message: str
    file_path: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScoringLog:
    experiment_id: str
    round: int
    metric: ScoringMetric
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConversationLog:
    experiment_id: str
    round: int
    agent_role: AgentRole
    target: str
    content: str
    originating_agent: str
    intervention: bool
    intervention_type: str | None = None
    intervention_reason: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExperimentLog:
    experiment_id: str
    description: str
    mode: str
    variant: str
    max_iterations: int
    stop_threshold: float
    model_engine: str
    evaluator_name: str
    evaluator_version: str
    final_score: float
    passed: bool
    reason_for_stop: str
    start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stop: datetime | None = None
