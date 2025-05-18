from __future__ import annotations

from enum import Enum


class SystemType(str, Enum):
    # Core Code Transformation
    LINTING = "linting"
    FORMATTING = "formatting"
    DOCSTRING = "docstring"
    TYPE_ANNOTATION = "type_annotation"
    REFACTORING = "refactoring"
    DEAD_CODE_REMOVAL = "dead_code_removal"
    COMPLEXITY_REDUCTION = "complexity_reduction"

    # Testing and Validation
    UNIT_TESTING = "unit_testing"
    EDGE_TESTING = "edge_testing"
    INTEGRATION_TESTING = "integration_testing"
    TEST_FIX_GENERATION = "test_fix_generation"
    MOCK_GENERATION = "mock_generation"
    STUB_EXTRACTION = "stub_extraction"

    # Observability and Instrumentation
    LOGGING_INJECTION = "logging_injection"
    TRACE_ANNOTATION = "trace_annotation"
    ERROR_HANDLING = "error_handling"

    # Documentation and Explanation
    INLINE_COMMENTING = "inline_commenting"
    FUNCTION_SUMMARIZATION = "function_summarization"
    FILE_SUMMARIZATION = "file_summarization"
    CHANGE_SUMMARIZATION = "change_summarization"

    # Review and Oversight
    CODE_REVIEW = "code_review"
    STATIC_ANALYSIS = "static_analysis"
    REGRESSION_ANALYSIS = "regression_analysis"
    MEDIATOR_RECONCILIATION = "mediator_reconciliation"
    SCORING_EVALUATION = "scoring_evaluation"

    # Planning and Organization
    SYMBOL_GRAPH_GENERATION = "symbol_graph_generation"
    DEPENDENCY_MAPPING = "dependency_mapping"
    FILE_RESTRUCTURING = "file_restructuring"
    FUNCTION_SPLITTING = "function_splitting"

    # MLOps-Specific
    DATA_VALIDATION = "data_validation"
    METADATA_ANNOTATION = "metadata_annotation"
    MODEL_DOC_GENERATION = "model_doc_generation"
    PIPELINE_TESTING = "pipeline_testing"
    TRAINING_CONFIG_AUDIT = "training_config_audit"
    FEATURE_TRACEABILITY = "feature_traceability"

    # Production Safety
    SECURITY_CHECK = "security_check"
    POLICY_COMPLIANCE = "policy_compliance"
    LICENSE_CHECK = "license_check"

    # Misc / Cross-cutting
    PATCHING = "patching"
    PROMPT_REFINEMENT = "prompt_refinement"
    AGENT_RECOMMENDATION = "agent_recommendation"
    SEMANTIC_DIFF = "semantic_diff"
    CONTEXT_FILTERING = "context_filtering"


class SystemState(Enum):
    """Finite state machine states for the CodeCritic system."""

    START = "start"
    GENERATE = "generate"
    DISCRIMINATE = "discriminate"
    MEDIATE = "mediate"
    PATCH = "patch"
    EVALUATE = "evaluate"
    END = "end"


class StateTransitionReason(str, Enum):
    FIRST_ROUND = "first_round"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    SCORE_THRESHOLD_MET = "score_threshold_met"
    SCORE_STAGNATION = "score_stagnation"
    AGENT_FAILURE = "agent_failure"
    MEDIATOR_OVERRIDE = "mediator_override"
    PATCH_RETRY = "patch_retry"
    CUSTOM_RULE = "custom_rule"
    END_REACHED = "end_reached"
