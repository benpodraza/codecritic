from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.agent_enums import AGENT
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class CodeStabilityStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        current = AGENT(state.get("state"))

        # If current state is START, transition to STABILITY state
        if current == AGENT.START:
            return {
                "state": AGENT.STABILITY,
                "reason": TRANSITION_REASON_TYPE.EVALUATING
            }

        # Get the decision from the agent's output, defaulting to UNKNOWN
        decision = getattr(agent_output, "decision", DECISION_TYPE.UNKNOWN)

        # Determine the next state and transition reason based on the decision
        transition_reason = (
            TRANSITION_REASON_TYPE.SUCCESSFUL if decision == DECISION_TYPE.ACCEPTED
            else TRANSITION_REASON_TYPE.UNSUCCESSFUL
        )

        # Return the transition details
        return {
            "state": AGENT.END,
            "state_type": STATE_TYPE.END,
            "decision": decision,
            "reason": transition_reason
        }
