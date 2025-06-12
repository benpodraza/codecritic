from app.enums.fsm_enums import DECISION_TYPE
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema

class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a generation round using the linting system prompt, context, and snapshot."""

    def _run(self, input: dict) -> AgentOutputSchema:
        file_path = input.get("file_path")
        system = input.get("system", "linting")

        if not self._prompt_provider:
            raise ValueError("Prompt provider is not set")
        if not self._agent_engine:
            raise ValueError("Agent engine is not set")

        final_prompt = self._prompt_provider.run(input=input)

        engine_output = self._agent_engine.run(
            input={
                "prompt": final_prompt,
                "before": file_path,
                "agent_type": self._config.agent_type,
                "agent_id": self._config.id,
                "system": system,
                "state_context": input.get("state_context", {}),
            }
        )

        response = engine_output.response
        log = self._extract_log(response) or "Generator agent did not return a log entry."
        code = self._extract_code(response)

        # Generator does not need to return a decision
        decision = DECISION_TYPE.ACCEPTED if code else DECISION_TYPE.UNKNOWN
        if decision == DECISION_TYPE.UNKNOWN:
            self._log.warning("⚠️ Generator did not return a code block; decision set to UNKNOWN.")

        return AgentOutputSchema(
            response=response,
            log=log,
            decision=decision,
            snapshot_id=None,
            file_path=file_path,
            score=getattr(engine_output, "score", None)
        )
