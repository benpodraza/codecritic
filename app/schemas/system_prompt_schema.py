from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from app.utilities.pydantic_compat import field_validator


class SystemPrompt(BaseModel):
    """Schema for the system_prompt table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    system_type: Optional[str] = None
    artifact_path: Optional[Path] = None

    table_name: str = "system_prompt"

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Optional[Path]) -> Optional[Path]:
        if v is None:
            return v
        p = Path(v)
        if not p.is_absolute() and ".." in p.parts:
            raise ValueError("artifact_path must be absolute or project relative")
        return p

    def model_dump(self, **kwargs) -> dict:
        return BaseModel.dict(self, **kwargs)
