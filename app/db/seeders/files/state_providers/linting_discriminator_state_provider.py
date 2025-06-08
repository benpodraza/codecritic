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

        # Handle the different decision types returned by the agent
        if agent_output.decision == DECISION_TYPE.ACCEPTED:
            return {
                "state": AGENT.END,
                "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,
                "decision": DECISION_TYPE.ACCEPTED,
                "file_path": agent_output.file_path,
            }

        elif agent_output.decision == DECISION_TYPE.IMPROVED:
            return {
                "state": AGENT.END,
                "reason": TRANSITION_REASON_TYPE.SUCCESSFUL,  # Could be improved, still valid
                "decision": DECISION_TYPE.IMPROVED,
                "file_path": agent_output.file_path,
            }

        # If the decision is REJECTED, handle accordingly
        return {
            "state": AGENT.END,
            "reason": TRANSITION_REASON_TYPE.UNSUCCESSFUL,
            "decision": DECISION_TYPE.REJECTED,
            "file_path": agent_output.file_path,
        }
