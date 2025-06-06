from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class CodeStabilityStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        if state.get("state") == "start":
            return {
                "state": "code_stability",
                "reason": "entering stability check"
            }

        decision = getattr(agent_output, "decision", DECISION_TYPE.UNKNOWN)
        result = "pass" if decision == DECISION_TYPE.ACCEPT else "fail"

        return {
            "state": "end",
            "state_type": STATE_TYPE.END,
            "decision": decision,
            "reason": "stability passed" if result == "pass" else "stability failed",
            "result": result
        }
