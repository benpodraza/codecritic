from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, validator

from .agent_prompt_schema import AgentPrompt
from .system_prompt_schema import SystemPrompt
from .context_provider_schema import ContextProvider


class PromptGenerator(BaseModel):
    """Schema for the prompt_generator table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    agent_prompt_id: Optional[int] = None
    system_prompt_id: Optional[int] = None
    content_provider_id: Optional[int] = None

    agent_prompt: Optional[AgentPrompt] = None
    system_prompt: Optional[SystemPrompt] = None
    content_provider: Optional[ContextProvider] = None
    artifact_path: Optional[Path] = None

    table_name: str = "prompt_generator"

    @validator("agent_prompt", always=True)
    def _sync_agent_prompt_id(cls, v, values):
        if v is not None and values.get("agent_prompt_id") is None:
            values["agent_prompt_id"] = getattr(v, "id", None)
        return v

    @validator("system_prompt", always=True)
    def _sync_system_prompt_id(cls, v, values):
        if v is not None and values.get("system_prompt_id") is None:
            values["system_prompt_id"] = getattr(v, "id", None)
        return v

    @validator("content_provider", always=True)
    def _sync_content_provider_id(cls, v, values):
        if v is not None and values.get("content_provider_id") is None:
            values["content_provider_id"] = getattr(v, "id", None)
        return v

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
        for field in ("agent_prompt", "system_prompt", "content_provider"):
            if data.get(field) is not None:
                data[field] = data[field].model_dump()
        if data.get("artifact_path") is not None:
            data["artifact_path"] = str(data["artifact_path"])
        return data
