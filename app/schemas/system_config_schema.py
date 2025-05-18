from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import model_validator

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

    table_name: str = "system_config"

    @model_validator(mode="after")
    def _sync_ids(self) -> "SystemConfig":
        if self.state_manager is not None and self.state_manager_id is None:
            self.state_manager_id = getattr(self.state_manager, "id", None)
        if self.scoring_model is not None and self.scoring_model_id is None:
            self.scoring_model_id = getattr(self.scoring_model, "id", None)
        return self

    def model_dump(self, **kwargs) -> dict:  # type: ignore[misc]
        return super().model_dump(**kwargs)  # type: ignore[misc]
