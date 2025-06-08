from enum import Enum


class STATE(str, Enum):
    START = "start"
    PREPROCESS = "preprocess"
    CODE_STABILITY = "code_stability"
    GENERATE = "generate"
    DISCRIMINATE = "discriminate"
    END = "end"