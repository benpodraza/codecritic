from pathlib import Path
from app.enums.fsm_enums import DECISION_TYPE
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema


class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a generation round using the linting system prompt, context, and snapshot."""
    def _run(self, input: dict) -> AgentOutputSchema:
        session_id = self._session_id
        file_path = input["file_path"]
        system = input.get("system", "linting")

        if not self._prompt_provider:
            raise ValueError("Prompt provider is not set")
        if not self._agent_engine:
            raise ValueError("Agent engine is not set")

        final_prompt = self._prompt_provider.run(
            input=input,
            session_id=session_id
        )

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
            DECISION_TYPE.ACCEPTED if "[AGENT_DECISION]accept" in response else
            DECISION_TYPE.REJECTED if "[AGENT_DECISION]reject" in response else
            DECISION_TYPE.UNKNOWN 
        )

        log = None
        if "[CONVERSATION_LOG_ENTRY]" in response:
            start = response.find("[CONVERSATION_LOG_ENTRY]") + len("[CONVERSATION_LOG_ENTRY]")
            end = response.find("[/CONVERSATION_LOG_ENTRY]")
            log = response[start:end].strip() if start < end else None

        code = self._extract_block(response, "[CODE]", "[/CODE]")
        log_entry = self._extract_block(response, "[CONVERSATION_LOG_ENTRY]", "[/CONVERSATION_LOG_ENTRY]")

        if decision == DECISION_TYPE.UNKNOWN and code and log_entry:
            decision = DECISION_TYPE.ACCEPTED
            self._log.debug("✅ Generator decision inferred as 'accept' based on presence of code and log.")
        elif decision == DECISION_TYPE.UNKNOWN :
            self._log.warning("⚠️ Generator decision remained 'unknown'; [AGENT_DECISION] tag may be missing.")

        # Ensure relative path if file_path is present
        relative_file_path = None
        if hasattr(engine_output, "file_path") and engine_output.file_path:
            try:
                relative_file_path = str(Path(engine_output.file_path).resolve().relative_to(Path.cwd()))
            except ValueError:
                relative_file_path = str(engine_output.file_path)

        return AgentOutputSchema(
            response=response,
            log=log,
            decision=decision,
            snapshot_id=engine_output.snapshot_id,
            file_path=relative_file_path,
            score=engine_output.score if hasattr(engine_output, "score") else None
        )
