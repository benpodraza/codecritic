from enum import Enum

class CONTROLLER(str, Enum):
    START = "start"
    END = "end"
    PREPROCESSING = "preprocessing_controller"
    TESTING = "testing_controller"
    OBSERVABILITY = "observability_controller"
    DOCUMENTATION = "documentation_controller"
    REVIEW = "review_controller"
    PLANNING = "planning_controller"
    MLOPS = "mlops_controller"
    SAFETY = "safety_controller"
    MISC = "misc_controller"