from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema

class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a GPT-4o generation round using the linting system prompt, context, and snapshot."""

    def __init__(self, config=None, engine=None, **kwargs):
        super().__init__(config=config, engine=engine, **kwargs)

    def _run(self, input: dict) -> AgentOutputSchema:
        session_id = self._session_id
        file_path = input["file_path"]
        system = input.get("system", "linting")

        if not self._prompt_provider:
            raise ValueError("Prompt provider is not set")
        if not self._agent_engine:
            raise ValueError("Agent engine is not set")

        # Build prompt
        final_prompt = self._prompt_provider.run(
            input=input,
            session_id=session_id
        )

        # Run engine
        engine_output = self._agent_engine.run(
            input={
                "prompt": final_prompt,
                "before": file_path,
                "agent_type": self.config.agent_type,
                "agent_id": self.config.id,
                "system": system,
                "state_context": input.get("state_context", {}),
            },
            session_id=session_id
        )

        decision = (
            "accept" if "[AGENT_DECISION]accept" in engine_output.response else
            "reject" if "[AGENT_DECISION]reject" in engine_output.response else
            "unknown"
        )

        log = None
        if "[CONVERSATION_LOG_ENTRY]" in engine_output.response:
            start = engine_output.response.find("[CONVERSATION_LOG_ENTRY]") + len("[CONVERSATION_LOG_ENTRY]")
            end = engine_output.response.find("[/CONVERSATION_LOG_ENTRY]")
            log = engine_output.response[start:end].strip() if start < end else None

        return AgentOutputSchema(
            response=engine_output.response,
            log=log,
            decision=decision,
            snapshot_id=None
        )
