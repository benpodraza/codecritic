from app.enums.logging_enums import RunContext  # ✅ Needed for context typing
from app.providers.context_provider_base import ContextProviderBase
from app.db.schemas import ContextOutputSchema

class BasicContextProvider(ContextProviderBase):
    def _run(self, input: dict, context: RunContext | None = None) -> ContextOutputSchema:
        return ContextOutputSchema(
            context={"file_path": input.get("file_path")},
            summary="Basic context with file_path only."
        )
