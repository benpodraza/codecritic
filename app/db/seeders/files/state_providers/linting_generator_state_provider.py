from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class LintingGeneratorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        current = state.get("state")
        decision = getattr(agent_output, "decision", DECISION_TYPE.UNKNOWN)

        if current == "start":
            return {
                "state": "generate",
                "reason": "entering generation step"
            }

        if current == "generate":
            return {
                "state": "end",
                "state_type": STATE_TYPE.END,
                "decision": decision,
                "reason": "generation complete",
                "result": "pass"
            }

        return {
            "state": "end",
            "state_type": STATE_TYPE.END,
            "decision": DECISION_TYPE.UNKNOWN,
            "reason": "unknown state",
            "result": "fail"
        }
