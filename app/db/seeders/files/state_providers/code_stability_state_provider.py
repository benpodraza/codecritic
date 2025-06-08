from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.agent_enums import AGENT
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class CodeStabilityStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        current = AGENT(state.get("state"))

        if current == AGENT.START:
            return {
                "state": AGENT.STABILITY,
                "reason": TRANSITION_REASON_TYPE.EVALUATING
            }

        decision = getattr(agent_output, "decision", DECISION_TYPE.UNKNOWN)

        return {
            "state": AGENT.END,
            "state_type": STATE_TYPE.END,
            "decision": decision,
            "reason": (
                TRANSITION_REASON_TYPE.PASSED
                if decision == DECISION_TYPE.ACCEPT
                else TRANSITION_REASON_TYPE.FAILED
            )
        }
