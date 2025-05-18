from __future__ import annotations

from pathlib import Path
from typing import Optional, ClassVar

from pydantic import BaseModel, validator

from .agent_engine_schema import AgentEngine
from .prompt_generator_schema import PromptGenerator


class AgentConfig(BaseModel):
    """Schema for the agent_config table."""

    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    agent_role: Optional[str] = None
    system_type: Optional[str] = None
    agent_engine_id: Optional[int] = None
    prompt_generator_id: Optional[int] = None
    agent_engine: Optional[AgentEngine] = None
    prompt_generator: Optional[PromptGenerator] = None
    artifact_path: Optional[Path] = None

    table_name: ClassVar[str] = "agent_config"

    @validator("agent_engine", always=True)
    def _sync_agent_engine_id(cls, v, values):
        if v is not None and values.get("agent_engine_id") is None:
            values["agent_engine_id"] = getattr(v, "id", None)
        return v

    @validator("prompt_generator", always=True)
    def _sync_prompt_gen_id(cls, v, values):
        if v is not None and values.get("prompt_generator_id") is None:
            values["prompt_generator_id"] = getattr(v, "id", None)
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
        for field in ("agent_engine", "prompt_generator"):
            if data.get(field) is not None:
                data[field] = data[field].model_dump()
        if data.get("artifact_path") is not None:
            data["artifact_path"] = str(data["artifact_path"])
        return data
