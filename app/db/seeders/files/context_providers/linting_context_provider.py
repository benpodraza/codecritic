from __future__ import annotations
from pathlib import Path
import json

from sqlalchemy.orm import Session
from app.enums.logging_enums import RunContext  # ✅ import context type
from app.providers.context_provider_base import ContextProviderBase
from app.utilities.metadata.logging.conversation_log import get_conversation_log
from app.db.schemas import ContextOutputSchema


class LintingContextProvider(ContextProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ContextOutputSchema:
        file_path = Path(input["file_path"]).resolve()
        system = input["system"]

        if not file_path.exists():
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        source_code = file_path.read_text(encoding="utf-8")

        # 🔧 propagate context
        score_result = self.score_provider.run(
            input={"file_path": str(file_path)},
            context=context
        )

        with Session(bind=self._engine) as session:
            convo_log = get_conversation_log(session, session_id=self._session_id, system=system)

        context_data = {
            "file_path": str(file_path),
            "source_code": source_code,
            "score": score_result.model_dump(),
            "conversation_log": convo_log
        }

        return ContextOutputSchema(
            context=context_data,
            summary=f"Context for {file_path.name}, {score_result.value} score, {len(convo_log)} log entries"
        )
