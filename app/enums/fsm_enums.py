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


class REASON_TYPE(str, Enum):
    """
    Reasons for state transitions in FSMs.

    - KICKOFF: Initial start of the flow
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed or was rejected
    - MAX_STEPS: Step limit reached
    - MANUAL_EXIT: User-initiated termination
    - UNSPECIFIED: Reason not explicitly stated
    """
    KICKOFF = "kickoff"
    SUCCESS = "success"
    FAILURE = "failure"
    MAX_STEPS = "max_steps"
    MANUAL_EXIT = "manual_exit"
    UNSPECIFIED = "unspecified"


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
    """
    Enumerated reasons for FSM state transitions.
    """
    FIRST_ROUND = "first_round"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    SCORE_THRESHOLD_MET = "score_threshold_met"
    SCORE_STAGNATION = "score_stagnation"
    AGENT_FAILURE = "agent_failure"
    MEDIATOR_OVERRIDE = "mediator_override"
    PATCH_RETRY = "patch_retry"
    CUSTOM_RULE = "custom_rule"
    END_REACHED = "end_reached"
