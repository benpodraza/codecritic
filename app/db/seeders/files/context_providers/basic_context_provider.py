from app.providers.context_provider_base import ContextProviderBase
from app.db.schemas import ContextOutputSchema

class BasicContextProvider(ContextProviderBase):
    def _run(self, input: dict) -> ContextOutputSchema:
        return ContextOutputSchema(
            context={"file_path": input.get("file_path")},
            summary="Basic context with file_path only."
        )
