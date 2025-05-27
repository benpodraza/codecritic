from app.providers.state_provider_base import StateProviderBase
from app.factories.agent_provider_factory import AgentProviderFactory
from app.db.models import AgentProviderConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.connection import DB_PATH
from pathlib import Path
from app.utilities.metadata.snapshots.snapshot_writer import SnapshotWriter

class LintingGeneratorStateProvider(StateProviderBase):
    """FSM state that invokes the linting generator agent."""

    def _run(self, input: dict) -> str:
        file_path = Path(input["file_path"])
        context = input["context"]
        session_id = self._session_id  # Now explicitly set in _transition()

        before_content = file_path.read_text(encoding="utf-8")

        engine = create_engine(f"sqlite:///{DB_PATH}")
        with Session(bind=engine) as session:
            row = session.query(AgentProviderConfig).filter_by(
                name="linting_generator_agent_provider"
            ).first()
            assert row, "❌ Agent provider not found"
            agent = AgentProviderFactory.create(row.id)

        agent_output = agent.run(
            input={"context": context, "file_path": str(file_path)},
            session_id=session_id
        )

        after_content = self.extract_code_block(agent_output)

        snapshot_writer = SnapshotWriter()
        snapshot_id = snapshot_writer.write_snapshot(
            before=before_content,
            after=after_content,
            session_id=session_id
        )

        self._log.debug(f"Snapshot ID created: {snapshot_id}")

        # Explicitly set the output
        self._output = agent_output

        return agent_output

    @staticmethod
    def extract_code_block(output: str) -> str:
        # First try [CODE] tags
        start = output.find("[CODE]")
        end = output.find("[/CODE]")

        if start != -1 and end != -1:
            return output[start + len("[CODE]"):end].strip()

        # If [CODE] tags aren't found, try triple backticks
        start_backticks = output.find("```python")
        end_backticks = output.find("```", start_backticks + len("```python"))

        if start_backticks != -1 and end_backticks != -1:
            return output[start_backticks + len("```python"):end_backticks].strip()

        raise ValueError(f"❌ No code block found in agent output:\n{output}")

    def _transition(self, state: dict) -> dict:
        # Explicitly ensure session_id is set once
        self._session_id = state.get("session_id", "notebook-dev-session")

        # Direct call to _run (no base run() invocation here!)
        self._run(state)

        return {
            **state,
            "state": "end",
            "output": getattr(self, "_output", "")
        }
