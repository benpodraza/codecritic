

from enum import Enum


class CONTROLLER(str, Enum):
    """
    Enum of high-level controllers grouping related SystemTypes.

    - PREPROCESSING: Core code transformation systems (linting, formatting, docstrings, etc.)
    - TESTING: Unit, edge, integration tests and related fix generation
    - OBSERVABILITY: Logging injection, trace annotation, error handling
    - DOCUMENTATION: Inline comments, function/file/change summarization
    - REVIEW: Code review, static analysis, regression analysis, mediator reconciliation
    - PLANNING: Symbol graphs, dependency mapping, restructuring, function splitting
    - MLOPS: Data validation, metadata, model docs, pipeline testing, training config audits, feature traceability
    - SAFETY: Security checks, policy compliance, license audits
    - MISC: Patching, prompt refinement, agent recommendation, semantic diff, context filtering
    """

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