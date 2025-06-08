from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, TRANSITION_REASON_TYPE
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import AgentOutputSchema

class LintingDiscriminatorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        if agent_output is None:
            return {
                "state": "discriminate",
                "reason": TRANSITION_REASON_TYPE.DISCRIMINATOR_STARTED  # Or a new one like FIRST_ROUND if you prefer
            }

        if agent_output.decision == DECISION_TYPE.ACCEPT:
            return {
                "state": "end",
                "reason": TRANSITION_REASON_TYPE.DISCRIMINATOR_ACCEPTED,
                "decision": DECISION_TYPE.ACCEPT,
                "file_path": agent_output.file_path,
            }

        return {
            "state": "end",
            "reason": TRANSITION_REASON_TYPE.DISCRIMINATOR_REJECTED,
            "decision": DECISION_TYPE.REJECT,
            "file_path": agent_output.file_path,
        }
