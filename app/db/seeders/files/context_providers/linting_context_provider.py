from __future__ import annotations
from pathlib import Path
import json

from sqlalchemy.orm import Session
from app.providers.context_provider_base import ContextProviderBase
from app.utilities.metadata.logging.conversation_log import get_conversation_log
from app.db.schemas import ContextOutputSchema


class LintingContextProvider(ContextProviderBase):
    def _run(self, input: dict) -> ContextOutputSchema:
        file_path = Path(input["file_path"]).resolve()
        system = input["system"]

        if not self._session_id:
            raise ValueError("ContextProvider requires session_id to be set on self")

        if not file_path.exists():
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        source_code = file_path.read_text(encoding="utf-8")

        score_result = self.score_provider.run(
            input={"file_path": str(file_path)},
            session_id=self._session_id
        )

        with Session(bind=self._engine) as session:
            convo_log = get_conversation_log(session, session_id=self._session_id, system=system)

        context = {
            "file_path": str(file_path),
            "source_code": source_code,
            "score": score_result.model_dump(),  # No 'pass' key inserted
            "conversation_log": convo_log
        }

        return ContextOutputSchema(
            context=context,
            summary=f"Context for {file_path.name}, {score_result.value} score, {len(convo_log)} log entries"
        )
