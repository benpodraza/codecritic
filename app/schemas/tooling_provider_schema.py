from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, validator


class ToolingProvider(BaseModel):
    """Schema for the tooling_provider table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    artifact_path: Optional[Path] = None

    table_name: str = "tooling_provider"

    @validator("artifact_path")
    def _check_path(cls, v: Optional[Path]) -> Optional[Path]:
        if v is None:
            return v
        p = Path(v)
        if not p.is_absolute() and ".." in p.parts:
            raise ValueError("artifact_path must be absolute or project relative")
        return p

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        data = self.dict()
        if data.get("artifact_path") is not None:
            data["artifact_path"] = str(data["artifact_path"])
        return data
