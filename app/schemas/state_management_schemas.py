from typing import Optional
from pydantic import BaseModel, Field

from app.enums.state_transition_enums import AgentRole, TransitionReason, TransitionTarget


class StateTransitionLog(BaseModel):
    experiment_id: str
    symbol: str
    round: int
    from_agent: Optional[AgentRole] = Field(default=None)
    to_agent: TransitionTarget
    reason: TransitionReason
    timestamp: str
    score_snapshot: Optional[dict] = None
    context_summary: Optional[dict] = None

