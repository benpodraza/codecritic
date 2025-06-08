from app.enums.fsm_enums import DECISION_TYPE, TRANSITION_REASON_TYPE
from app.enums.agent_enums import AGENT
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class LintingDiscriminatorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        if agent_output is None:
            return {
                "state": AGENT.DISCRIMINATOR,
                "reason": TRANSITION_REASON_TYPE.INITIALIZATION
            }

        if agent_output.decision == DECISION_TYPE.ACCEPT:
            return {
                "state": AGENT.END,
                "reason": TRANSITION_REASON_TYPE.PASSED,
                "decision": DECISION_TYPE.ACCEPT,
                "file_path": agent_output.file_path,
            }

        return {
            "state": AGENT.END,
            "reason": TRANSITION_REASON_TYPE.FAILED,
            "decision": DECISION_TYPE.REJECT,
            "file_path": agent_output.file_path,
        }
