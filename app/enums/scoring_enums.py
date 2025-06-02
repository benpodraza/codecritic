from enum import Enum

class SCORING_METRIC_TYPE(str, Enum):
    LINTING_SCORE = "linting_score"
    CODE_STABILITY_SCORE = "code_stability_score"
