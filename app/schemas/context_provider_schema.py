from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, validator

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

    @validator("tooling_provider", always=True)
    def _check_fk(cls, v, values):
        if v is not None and values.get("tooling_provider_id") is None:
            values["tooling_provider_id"] = getattr(v, "id", None)
        return v

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = self.dict()
        if data.get("tooling_provider") is not None:
            data["tooling_provider"] = data["tooling_provider"].model_dump()
        return data
