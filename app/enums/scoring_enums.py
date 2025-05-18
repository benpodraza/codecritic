from enum import Enum


class ScoringMetric(str, Enum):
    FUNCTIONAL_CORRECTNESS = "functional_correctness"
    MAINTAINABILITY_INDEX = "maintainability_index"
    BUG_FIX_SUCCESS = "bug_fix_success_rate"
    LINTING_COMPLIANCE = "linting_compliance"
    AGENT_SUCCESS_RATE = "agent_role_success_rate"
    RETRY_SUCCESS_RATE = "retry_success_rate"
    COVERAGE = "coverage"
