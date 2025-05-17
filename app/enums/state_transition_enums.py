from enum import Enum, auto

class TransitionReason(str, Enum):
    FIRST_ROUND = "first_round"
    SCORE_STAGNATION = "score_stagnation"
    MEDIATOR_OVERRIDE = "mediator_override"
    NORMAL_SEQUENCE = "normal_sequence"
    CUSTOM_RULE = "custom_rule"

class TransitionTarget(str, Enum):
    START = "START"
    GENERATOR = "GENERATE"
    DISCRIMINATOR = "DISCRIMINATE"
    MEDIATOR = "MEDIATE"
    PATCHOR = "PATCHOR"
    RECOMMENDER = "RECOMMENDER"
    END = "END"

    
