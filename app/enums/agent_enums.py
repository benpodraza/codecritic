from __future__ import annotations

from enum import Enum


class AgentRole(str, Enum):
    GENERATOR = "generator"
    DISCRIMINATOR = "discriminator"
    MEDIATOR = "mediator"
    PATCHER = "patcher"
    EVALUATOR = "evaluator"
    RECOMMENDER = "recommender"
