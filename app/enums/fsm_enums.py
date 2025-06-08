from enum import Enum


class STATE_TYPE(str, Enum):
    """
    Types of states within a finite state machine.

    - START: Entry point to the FSM
    - INTERMEDIATE: Transitional state with more steps to come
    - END: Final terminating state
    """
    START = "start"
    INTERMEDIATE = "intermediate"
    END = "end"


class STATE_DECISION_TYPE(str, Enum):
    INITIAL = "initial"
    IMPROVED = "improved"
    REJECTED = "rejected"
    FINAL = "final"
    UNKNOWN = "unknown"


class DECISION_TYPE(str, Enum):
    """
    Discriminator or agent decision about a code action.

    - ACCEPT: Changes are valid and accepted
    - REJECT: Changes are invalid or insufficient
    - UNKNOWN: No decision made or undecidable
    """
    ACCEPT = "accept"
    REJECT = "reject"
    UNKNOWN = "unknown"


class TRANSITION_REASON_TYPE(str, Enum):
    PROGRAM_INIT = "program_init"
    PREPROCESSING_COMPLETE = "preprocessing_complete"
    KICKOFF = "kickoff"
    CONTROLLER_FINISHED = "controller_finished"
    STABILITY_CHECK = "stability_check"
    STABILITY_PASSED = "stability_passed"
    STABILITY_FAILED = "stability_failed"
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    POST_GEN_STABILITY_PASSED = "post_gen_stability_passed"
    POST_GEN_STABILITY_FAILED = "post_gen_stability_failed"
    DISCRIMINATOR_STARTED = "discriminator_started"
    DISCRIMINATOR_ACCEPTED = "discriminator_accepted"
    DISCRIMINATOR_REJECTED = "discriminator_rejected"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    END_REACHED = "end_reached"
    AGENT_FAILURE = "agent_failure"
    CUSTOM_RULE = "custom_rule"

