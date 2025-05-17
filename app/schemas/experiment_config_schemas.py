# app/config/experiment_config_schema.py

from pydantic import BaseModel
from typing import Optional, Dict
from enum import Enum

from app.schemas.agent_config_schema import AgentConfig

class SystemType(str, Enum):
    PREPROCESSING = "Preprocessing"
    TRAINING = "Training"
    EVALUATION = "Evaluation"

class CodeStyle(str, Enum):
    AI_FIRST = "ai_first"
    HUMAN_FIRST = "human_first"

class ScoringModel(str, Enum):
    HEURISTIC_V1 = "heuristic-v1"
    GPT_EVAL = "openai/gpt-4-eval"

class EvaluatorConfig(BaseModel):
    name: str  # e.g., "static_code_evaluator"
    version: str  # e.g., "v1"

class ExperimentConfig(BaseModel):
    experiment_id: str
    run_id: str
    system: SystemType
    description: str
    code_style: CodeStyle
    max_lines_per_function: int

    generator: AgentConfig
    discriminator: Optional[AgentConfig]
    mediator: Optional[AgentConfig]
    patchor: Optional[AgentConfig]
    recommender: Optional[AgentConfig]
    
    evaluator: EvaluatorConfig
    scoring_model: ScoringModel
