# app/utils/logging/schemas.py

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime, timezone

class StateTransitionLog(BaseModel):
    experiment_id: str
    run_id: str
    round: int
    from_state: Literal["START", "GENERATE", "DISCRIMINATE", "MEDIATE", "PATCHOR", "RECOMMENDER"]
    to_state: Literal["GENERATE", "DISCRIMINATE", "MEDIATE", "PATCHOR", "RECOMMENDER", "END"]
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StateLog(BaseModel):
    experiment_id: str
    run_id: str
    system: str
    round: int
    state: Literal["START", "GENERATE", "DISCRIMINATE", "MEDIATE", "PATCHOR", "RECOMMENDER", "END"]
    action: str
    score: Optional[dict]
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PromptLog(BaseModel):
    experiment_id: str
    run_id: str
    round: int
    system: str
    agent_role: str
    agent_engine: str
    symbol: str
    prompt: str
    response: str
    start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stop: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationLog(BaseModel):
    experiment_id: str
    run_id: str
    round: int
    agent_role: str
    target: str
    content: str
    originating_agent: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ErrorLog(BaseModel):
    experiment_id: str
    run_id: str
    round: int
    error_type: str
    message: str
    file_path: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExperimentLog(BaseModel):
    experiment_id: str
    description: str
    mode: str
    variant: str
    max_iterations: int
    stop_threshold: float
    model_engine: str
    evaluator_name: Optional[str] = None
    evaluator_version: Optional[str] = None
    final_score: Optional[float] = None
    passed: Optional[bool] = None
    reason_for_stop: Optional[str] = None
    start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stop: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationLog(BaseModel):
    experiment_id: str
    run_id: str
    round: int
    symbol: str
    final: bool
    score: float
    passed: bool
    evaluator_name: str
    evaluator_version: str
    diagnostics: Optional[dict] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

