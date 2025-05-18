from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, validator

from .system_config_schema import SystemConfig
from .scoring_provider_schema import ScoringProvider


class ExperimentConfig(BaseModel):
    """Schema for the experiment_config table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    system_manager_id: Optional[int] = None
    scoring_model_id: Optional[int] = None

    system_manager: Optional[SystemConfig] = None
    scoring_model: Optional[ScoringProvider] = None

    table_name: str = "experiment_config"

    @validator("system_manager", always=True)
    def _sync_system_manager_id(cls, v, values):
        if v is not None and values.get("system_manager_id") is None:
            values["system_manager_id"] = getattr(v, "id", None)
        return v

    @validator("scoring_model", always=True)
    def _sync_scoring_model_id(cls, v, values):
        if v is not None and values.get("scoring_model_id") is None:
            values["scoring_model_id"] = getattr(v, "id", None)
        return v

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = self.dict()
        for field in ("system_manager", "scoring_model"):
            if data.get(field) is not None:
                data[field] = data[field].model_dump()
        return data
