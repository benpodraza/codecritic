from app.enums.fsm_enums import DECISION_TYPE
from app.enums.logging_enums import RunContext
from app.providers.agent_provider_base import AgentProviderBase
from app.db.schemas import AgentOutputSchema, SnapshotContext
from app.utilities.metadata.snapshots.snapshot_archive import SnapshotArchive
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE
fm = get_file_manager()

class LintingGeneratorAgentProvider(AgentProviderBase):
    """Runs a generation round using the linting system prompt, context, and snapshot."""

    def _run(self, input: dict, context: RunContext | None = None) -> AgentOutputSchema:
        file_path = input.get("file_path")
        system = input.get("system", "linting")

        if not self._prompt_provider:
            raise ValueError("Prompt provider is not set")
        if not self._agent_engine:
            raise ValueError("Agent engine is not set")

        # 🔧 Generate prompt and run engine
        prompt_output = self._prompt_provider.run(input=input, context=context)
        engine_output = self._agent_engine.run(
            input={
                "prompt": prompt_output.prompt,
                "file_path": file_path,
                "agent_type": self._config.agent_type,
                "agent_id": self._config.id,
                "system": system,
                "state_context": input.get("state_context", {}),
            },
            context=context,
            prompt_provider=self._prompt_provider  # 👈 passed directly, not via input
        )

        resolved_before_path = fm._resolve(FILETYPE.WORKING, file_path)

        # 🔧 Record snapshot with logical path
        snapshot = SnapshotContext(
            context=context,
            decision=engine_output.decision,
            log=engine_output.log,
            state=input.get("state_context", {}).get("state", "unknown"),
            agent_name=self._config.name,
            system=system,
            before_path=resolved_before_path,    # <- FIX
            after_content=engine_output.content,
        )

        snapshot_id = SnapshotArchive(self._engine).record(snapshot=snapshot)

        return AgentOutputSchema(
            response=engine_output.response,
            log=engine_output.log,
            decision=DECISION_TYPE(engine_output.decision),
            snapshot_id=snapshot_id,
            file_path=file_path,
            score=getattr(engine_output, "score", None)
        )
