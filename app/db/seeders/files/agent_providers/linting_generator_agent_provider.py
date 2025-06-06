from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema


class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a GPT-4o generation round using the linting system prompt, context, and snapshot."""
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
                "agent_type": self._config.agent_type,
                "agent_id": self._config.id,
                "system": system,
                "state_context": input.get("state_context", {}),
            },
            session_id=session_id
        )

        response = engine_output.response
        decision = (
            "accept" if "[AGENT_DECISION]accept" in response else
            "reject" if "[AGENT_DECISION]reject" in response else
            "unknown"
        )

        # Try to extract log and code blocks
        log = None
        if "[CONVERSATION_LOG_ENTRY]" in response:
            start = response.find("[CONVERSATION_LOG_ENTRY]") + len("[CONVERSATION_LOG_ENTRY]")
            end = response.find("[/CONVERSATION_LOG_ENTRY]")
            log = response[start:end].strip() if start < end else None

        code = self._extract_block(response, "[CODE]", "[/CODE]")
        log_entry = self._extract_block(response, "[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")

        # 🧠 Infer accept if valid code and log but no explicit decision
        if decision == "unknown" and code and log_entry:
            decision = "accept"
            self._log.debug("✅ Generator decision inferred as 'accept' based on presence of code and log.")
        elif decision == "unknown":
            self._log.warning("⚠️ Generator decision remained 'unknown'; [AGENT_DECISION] tag may be missing.")

        return AgentOutputSchema(
            response=response,
            log=log,
            decision=decision,
            snapshot_id=engine_output.snapshot_id,
            file_path=engine_output.file_path if hasattr(engine_output, "file_path") else None,
            score=engine_output.score if hasattr(engine_output, "score") else None
        )

