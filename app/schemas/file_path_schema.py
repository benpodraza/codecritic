from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel
from app.utilities.pydantic_compat import field_validator


class FilePath(BaseModel):
    """Schema for file paths tracked in the database."""

    artifact_path: Path

    table_name: str = "file_path"

    @field_validator("artifact_path")
    @classmethod
    def _check_path(cls, v: Path) -> Path:
        p = Path(v)
        if not p.is_absolute() and ".." in p.parts:
            raise ValueError("artifact_path must be absolute or project relative")
        return p

    def model_dump(self, **kwargs) -> dict:  # type: ignore[misc]
        return super().model_dump(**kwargs)  # type: ignore[misc]
