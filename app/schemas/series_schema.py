from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, validator

from .experiment_config_schema import ExperimentConfig


class Series(BaseModel):
    """Schema for the series table."""

    id: Optional[int] = None
    experiment_config_id: Optional[int] = None
    experiment_config: Optional[ExperimentConfig] = None

    table_name: str = "series"

    @validator("experiment_config", always=True)
    def _sync_experiment_id(cls, v, values):
        if v is not None and values.get("experiment_config_id") is None:
            values["experiment_config_id"] = getattr(v, "id", None)
        return v

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = self.dict()
        if data.get("experiment_config") is not None:
            data["experiment_config"] = data["experiment_config"].model_dump()
        return data
