from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import model_validator

from .tooling_provider_schema import ToolingProvider


class ContextProvider(BaseModel):
    """Schema for the context_provider table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    system_type: Optional[str] = None
    tooling_provider_id: Optional[int] = None
    tooling_provider: Optional[ToolingProvider] = None

    table_name: str = "context_provider"

    @model_validator(mode="after")
    def _sync_ids(self) -> "ContextProvider":
        if self.tooling_provider is not None and self.tooling_provider_id is None:
            self.tooling_provider_id = getattr(self.tooling_provider, "id", None)
        return self

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = getattr(super(), "model_dump", super().dict)()
        if data.get("tooling_provider") is not None:
            data["tooling_provider"] = data["tooling_provider"].model_dump()
        return data
