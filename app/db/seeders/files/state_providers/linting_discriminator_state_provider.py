from __future__ import annotations
from app.providers.state_provider_base import StateProviderBase
from app.db.schemas import StateOutputSchema, AgentOutputSchema
from app.enums.fsm_enums import STATE_TYPE, DECISION_TYPE, REASON_TYPE
from app.enums.system_enums import STATE_DECISION_TYPE

class LintingDiscriminatorStateProvider(StateProviderBase):
    def _transition(self, state: dict, agent_output: AgentOutputSchema | None) -> dict:
        if agent_output is None:
            return {
                "state": "discriminate",
                "reason": "starting discriminator round"
            }

        if agent_output.decision == DECISION_TYPE.ACCEPT:
            return {
                "state": "end",
                "reason": "discriminator accepted change",
                "decision": DECISION_TYPE.ACCEPT,
                "file_path": agent_output.file_path,
                "score": agent_output.score
            }
        else:
            return {
                "state": "end",
                "reason": "discriminator rejected the change",
                "decision": DECISION_TYPE.REJECT
            }
