from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Unified list of metric names expected in experiment results
EVALUATION_METRICS = [
    "bug_fix_success_rate",
    "functional_correctness",
    "avg_test_pass_rate",
    "maintainability_index",
    "cyclomatic_complexity",
    "linting_compliance_rate",
    "iterations_to_convergence",
    "intervention_frequency",
    "agent_role_success_rate",
    "retry_success_rate",
    "mediation_success_rate",
]


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def compute_metrics(
    evaluation_logs: List[Any],
    code_quality_logs: List[Any],
    conversation_logs: List[Any],
    prompt_logs: List[Any],
    state_logs: List[Any],
) -> Dict[str, float]:
    """Compute experiment metrics from structured logs."""

    logger.debug(
        "Computing metrics: evaluations=%d quality=%d conversation=%d prompts=%d states=%d",
        len(evaluation_logs),
        len(code_quality_logs),
        len(conversation_logs),
        len(prompt_logs),
        len(state_logs),
    )

    metrics: Dict[str, float] = {}

    bug_fixes = [_get(log, "bug_fixed", False) for log in evaluation_logs]
    metrics["bug_fix_success_rate"] = _avg([1.0 for bug in bug_fixes if bug])

    func_correct = [_get(log, "all_tests_passed", False) for log in evaluation_logs]
    metrics["functional_correctness"] = _avg([1.0 for passes in func_correct if passes])

    pass_rates = []
    for log in evaluation_logs:
        total = _get(log, "tests_total", 0)
        passed = _get(log, "tests_passed", 0)
        if total:
            pass_rates.append(passed / total)
    metrics["avg_test_pass_rate"] = _avg(pass_rates)

    mi_values = [_get(log, "maintainability_index", 0.0) for log in code_quality_logs]
    metrics["maintainability_index"] = _avg(mi_values)

    cc_values = [_get(log, "cyclomatic_complexity", 0.0) for log in code_quality_logs]
    metrics["cyclomatic_complexity"] = _avg(cc_values)

    lint_compliance = [
        1.0 if _get(log, "lint_errors", 1) == 0 else 0.0 for log in code_quality_logs
    ]
    metrics["linting_compliance_rate"] = _avg(lint_compliance)

    rounds = [_get(log, "round", 0) for log in state_logs]
    metrics["iterations_to_convergence"] = max(rounds) + 1 if rounds else 0.0

    interventions = [
        1.0 for log in conversation_logs if _get(log, "intervention", False)
    ]
    metrics["intervention_frequency"] = _avg(interventions)

    outcomes = [_get(log, "agent_action_outcome", None) for log in prompt_logs]
    successes = [1.0 for o in outcomes if o == "success"]
    metrics["agent_role_success_rate"] = _avg(successes)

    retry_logs = [log for log in prompt_logs if _get(log, "attempt_number", 0) > 0]
    retry_successes = [
        1.0
        for log in retry_logs
        if _get(log, "agent_action_outcome", None) == "success"
    ]
    metrics["retry_success_rate"] = _avg(retry_successes)

    mediation_logs = [
        log
        for log in conversation_logs
        if _get(log, "intervention_type", None) == "mediation"
    ]
    mediation_success = [
        1.0 for log in mediation_logs if _get(log, "intervention", False)
    ]
    metrics["mediation_success_rate"] = _avg(mediation_success)

    logger.info("Metrics computed: %s", metrics)
    return metrics
