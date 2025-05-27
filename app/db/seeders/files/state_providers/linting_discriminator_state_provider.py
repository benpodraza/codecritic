from app.providers.state_provider_base import StateProviderBase
from app.factories.agent_provider_factory import AgentProviderFactory
from app.db.models import AgentProviderConfig
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.db.connection import DB_PATH
from app.utilities.metadata.snapshots.snapshot_reader import read_latest_snapshot
from pathlib import Path

class LintingDiscriminatorStateProvider(StateProviderBase):

    def _run(self, input: dict) -> str:
        session_id = self._session_id
        system = self._system
        engine = create_engine(f"sqlite:///{DB_PATH}")

        with Session(bind=engine) as session:
            row = session.query(AgentProviderConfig).filter_by(
                name="linting_discriminator_agent_provider"
            ).first()
            assert row, "❌ Discriminator agent not found"
            agent = AgentProviderFactory.create(row.id)

        result = agent.run(
            input={"system": system},
            session_id=session_id
        )

        self._output = result
        return result

    def _transition(self, state: dict) -> dict:
        output = getattr(self, "_output", "")
        accepted = "[AGENT_DECISION]accept[/AGENT_DECISION]" in output

        if accepted:
            snapshot = read_latest_snapshot(session_id=self._session_id)
            after = snapshot.get("after")
            output_path = state["file_path"]
            Path(output_path).write_text(after, encoding="utf-8")

        return {
            **state,
            "state": "end",
            "discriminator_decision": "accept" if accepted else "reject",
            "output": output
        }
