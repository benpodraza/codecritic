from __future__ import annotations

from typing import Optional

from typing import ClassVar

from pydantic import BaseModel, validator

from .state_manager_schema import StateManager
from .scoring_provider_schema import ScoringProvider


class SystemConfig(BaseModel):
    """Schema for the system_config table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    system_type: Optional[str] = None
    state_manager_id: Optional[int] = None
    scoring_model_id: Optional[int] = None

    state_manager: Optional[StateManager] = None
    scoring_model: Optional[ScoringProvider] = None

    table_name: ClassVar[str] = "system_config"

    @validator("state_manager", always=True)
    def _sync_state_manager_id(cls, v, values):
        if v is not None and values.get("state_manager_id") is None:
            values["state_manager_id"] = getattr(v, "id", None)
        return v

    @validator("scoring_model", always=True)
    def _sync_scoring_model_id(cls, v, values):
        if v is not None and values.get("scoring_model_id") is None:
            values["scoring_model_id"] = getattr(v, "id", None)
        return v

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = self.dict()
        for field in ("state_manager", "scoring_model"):
            if data.get(field) is not None:
                data[field] = data[field].model_dump()
        return data
