from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import model_validator

from .experiment_config_schema import ExperimentConfig


class Series(BaseModel):
    """Schema for the series table."""

    id: Optional[int] = None
    experiment_config_id: Optional[int] = None
    experiment_config: Optional[ExperimentConfig] = None

    table_name: str = "series"

    @model_validator(mode="after")
    def _sync_ids(self) -> "Series":
        if self.experiment_config is not None and self.experiment_config_id is None:
            self.experiment_config_id = getattr(self.experiment_config, "id", None)
        return self

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = getattr(super(), "model_dump", super().dict)()
        if data.get("experiment_config") is not None:
            data["experiment_config"] = data["experiment_config"].model_dump()
        return data
