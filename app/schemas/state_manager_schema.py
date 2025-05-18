from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import field_validator


class StateManager(BaseModel):
    """Schema for the state_manager table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    system_state: Optional[str] = None
    system_type: Optional[str] = None
    agent_id: Optional[int] = None
    artifact_path: Optional[Path] = None

    table_name: str = "state_manager"

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Optional[Path]) -> Optional[Path]:
        if v is None:
            return v
        p = Path(v)
        if not p.is_absolute() and ".." in p.parts:
            raise ValueError("artifact_path must be absolute or project relative")
        return p

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = getattr(super(), "model_dump", super().dict)()
        if data.get("artifact_path") is not None:
            data["artifact_path"] = str(data["artifact_path"])
        return data
