from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.agent_enums import AGENT
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class LintingGeneratorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        current = AGENT(state.get("state"))

        if current == AGENT.START:
            return {
                "state": AGENT.GENERATOR,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION
            }

        if current == AGENT.GENERATOR:
            return {
                "state": AGENT.END,
                "state_type": STATE_TYPE.END,
                "decision": DECISION_TYPE.UNKNOWN,
                "reason": TRANSITION_REASON_TYPE.SUCCESSFUL
            }

        return {
            "state": AGENT.END,
            "state_type": STATE_TYPE.END,
            "decision": DECISION_TYPE.UNKNOWN,
            "reason": TRANSITION_REASON_TYPE.CUSTOM_RULE
        }
