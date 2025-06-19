from __future__ import annotations
import json
import uuid

from sqlalchemy.orm import Session

from app.enums.logging_enums import RunContext
from app.providers.context_provider_base import ContextProviderBase
from app.utilities.metadata.logging.conversation_log import get_conversation_log
from app.db.schemas import ContextOutputSchema
from app.utilities.file_management.file_utils import get_file_manager, FILETYPE

fm = get_file_manager()


class LintingContextProvider(ContextProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ContextOutputSchema:
        file_path = input["file_path"]

        try:
            resolved_name, resolved_type = self._resolve_file_path(file_path)
            source_code = fm.load(resolved_type, resolved_name)
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ File not found: {file_path}")

        score_result = self.score_provider.run(
            input={"file_path": resolved_name},
            context=context
        )

        with Session(bind=self._engine) as session:
            convo_log = get_conversation_log(
                session=session,
                session_id=self._session_id,
                file_log_id=context.file_log_id
            )

        context_data = {
            "file_path": resolved_name,
            "source_code": source_code,
            "score": score_result.model_dump(),
            "conversation_log": convo_log
        }

        return ContextOutputSchema(
            context=context_data,
            summary=f"Context for {resolved_name}, {score_result.value} score, {len(convo_log)} log entries"
        )

    def _resolve_file_path(self, maybe_code: str) -> tuple[str, FILETYPE]:
        if "\n" not in maybe_code:
            try:
                for ft in [FILETYPE.WORKING, FILETYPE.SNAPSHOT, FILETYPE.INPUT]:
                    candidate = fm._resolve(ft, maybe_code)
                    if candidate.exists():
                        return maybe_code, ft
            except Exception:
                pass

        name = f"{uuid.uuid4().hex}.py"
        fm.save(FILETYPE.SNAPSHOT, name, maybe_code)
        return name, FILETYPE.SNAPSHOT

