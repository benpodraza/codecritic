from __future__ import annotations
import json

from sqlalchemy.orm import Session

from app.enums.logging_enums import RunContext
from app.providers.context_provider_base import ContextProviderBase
from app.utilities.metadata.logging.conversation_log import get_conversation_log
from app.db.schemas import ContextOutputSchema
from app.utilities.file_management.file_utils import get_file_manager

fm = get_file_manager()


class LintingContextProvider(ContextProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ContextOutputSchema:
        file_path = input["file_path"]

        try:
            resolved_type = fm.resolve_existing_filetype(file_path)
            source_code = fm.load(resolved_type, file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        score_result = self.score_provider.run(
            input={"file_path": file_path},
            context=context
        )

        with Session(bind=self._engine) as session:
            convo_log = get_conversation_log(
                session=session,
                session_id=self._session_id,
                file_log_id=context.file_log_id
            )

        context_data = {
            "file_path": file_path,
            "source_code": source_code,
            "score": score_result.model_dump(),
            "conversation_log": convo_log
        }

        return ContextOutputSchema(
            context=context_data,
            summary=f"Context for {file_path}, {score_result.value} score, {len(convo_log)} log entries"
        )
