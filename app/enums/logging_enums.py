from enum import Enum


class LogType(str, Enum):
    EXPERIMENT = "experiment"
    STATE = "state"
    STATE_TRANSITION = "state_transition"
    PROMPT = "prompt"
    CONVERSATION = "conversation"
    SCORING = "scoring"
    CODE_QUALITY = "code_quality"
    ERROR = "error"
    RECOMMENDATION = "recommendation"
    FEEDBACK = "feedback"
    PROMPT_GENERATION = "prompt_generation"
