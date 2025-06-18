from app.enums.fsm_enums import DECISION_TYPE
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema
from app.enums.logging_enums import RunContext 

class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a generation round using the linting system prompt, context, and snapshot."""

    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:        
        file_path = input.get("file_path")
        system = input.get("system", "linting")

        if not self._prompt_provider:
            raise ValueError("Prompt provider is not set")
        if not self._agent_engine:
            raise ValueError("Agent engine is not set")

        # 🔧 Propagate context to prompt provider
        final_prompt = self._prompt_provider.run(input=input, context=context)

        # 🔧 Propagate context to agent engine
        engine_output = self._agent_engine.run(
            input={
                "prompt": final_prompt,
                "before": file_path,
                "agent_type": self._config.agent_type,
                "agent_id": self._config.id,
                "system": system,
                "state_context": input.get("state_context", {}),
            },
            context=context
        )

        response = engine_output.response
        log = self._extract_log(response) or "Generator agent did not return a log entry."
        code = self._extract_code(response)

        return AgentOutputSchema(
            response=response,
            log=log,
            decision=DECISION_TYPE.UNKNOWN,
            snapshot_id=None,
            file_path=file_path,
            score=getattr(engine_output, "score", None)
        )
