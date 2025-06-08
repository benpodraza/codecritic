from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class CodeStabilityStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        if state.get("state") == "start":
            return {
                "state": "code_stability",
                "reason": TRANSITION_REASON_TYPE.STABILITY_CHECK
            }

        decision = getattr(agent_output, "decision", DECISION_TYPE.UNKNOWN)

        return {
            "state": "end",
            "state_type": STATE_TYPE.END,
            "decision": decision,
            "reason": (
                TRANSITION_REASON_TYPE.STABILITY_PASSED
                if decision == DECISION_TYPE.ACCEPT
                else TRANSITION_REASON_TYPE.STABILITY_FAILED
            )
        }
