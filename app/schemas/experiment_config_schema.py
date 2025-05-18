from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import model_validator

from .system_config_schema import SystemConfig
from .scoring_provider_schema import ScoringProvider


class ExperimentConfig(BaseModel):
    """Schema for the experiment_config table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    system_manager_id: Optional[int | str] = None
    scoring_model_id: Optional[int | str] = None

    system_manager: Optional[SystemConfig] = None
    scoring_model: Optional[ScoringProvider] = None

    table_name: str = "experiment_config"

    @model_validator(mode="after")
    def _sync_ids(self) -> "ExperimentConfig":
        if self.system_manager is not None and self.system_manager_id is None:
            self.system_manager_id = getattr(self.system_manager, "id", None)
        if self.scoring_model is not None and self.scoring_model_id is None:
            self.scoring_model_id = getattr(self.scoring_model, "id", None)
        return self

    def model_dump(self, **kwargs) -> dict:
        return BaseModel.dict(self, **kwargs)
