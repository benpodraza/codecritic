from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, validator


class FilePath(BaseModel):
    """Schema for file paths tracked in the database."""

    artifact_path: Path

    table_name: ClassVar[str] = "file_path"

    @validator("artifact_path")
    def _check_path(cls, v: Path) -> Path:
        p = Path(v)
        if not p.is_absolute() and ".." in p.parts:
            raise ValueError("artifact_path must be absolute or project relative")
        return p

    def model_dump(self) -> dict:  # pragma: no cover - simple wrapper
        return {"artifact_path": str(self.artifact_path)}
