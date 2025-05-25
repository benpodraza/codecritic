# from pydantic import BaseModel, Field
# from pathlib import Path
# from typing import Dict, List, Optional, ClassVar
# from uuid import UUID, uuid4
# from app.enums.system_enums import SystemType
# from app.utilities.pydantic_compat import field_validator

# class AgentPromptSchema(BaseModel):
#     id: Optional[int]
#     guid: UUID = Field(default_factory=uuid4)
#     name: str
#     description: Optional[str]
#     artifact_path: Path
#     tags: Optional[List[str]] = None

#     table_name: ClassVar[str] = "agent_prompt"

#     @field_validator("artifact_path")
#     @classmethod
#     def _check_path(cls, v: Path) -> Path:
#         if not v.is_absolute() and ".." in v.parts:
#             raise ValueError("Invalid artifact path")
#         return v

# class SystemPromptSchema(BaseModel):
#     id: Optional[int]
#     guid: UUID = Field(default_factory=uuid4)
#     name: str
#     system_type: SystemType
#     description: Optional[str]
#     artifact_path: Path
#     tags: Optional[List[str]] = None

#     table_name: ClassVar[str] = "system_prompt"

#     @field_validator("artifact_path")
#     @classmethod
#     def _check_path(cls, v: Path) -> Path:
#         if not v.is_absolute() and ".." in v.parts:
#             raise ValueError("Invalid artifact path")
#         return v

# class ToolConfig(BaseModel):
#     id: Optional[int] = None
#     guid: UUID = Field(default_factory=uuid4)
#     name: str
#     description: Optional[str] = None
#     config: Optional[Dict] = None
#     artifact_path: Path

#     table_name: ClassVar[str] = "tool_config"

#     @field_validator("artifact_path")
#     @classmethod
#     def _check_path(cls, v: Path) -> Path:
#         if not v.is_absolute() and ".." in v.parts:
#             raise ValueError("Invalid artifact path")
#         return v

# class ScoreProvider(BaseModel):
#     id: Optional[int] = None
#     guid: UUID = Field(default_factory=uuid4)
#     name: str
#     description: Optional[str] = None
#     artifact_path: Optional[Path] = None

#     table_name: ClassVar[str] = "score_provider"

#     @field_validator("artifact_path")
#     @classmethod
#     def _check_path(cls, v: Optional[Path]) -> Optional[Path]:
#         if v is None:
#             return v
#         p = Path(v)
#         if not p.is_absolute() and ".." in p.parts:
#             raise ValueError("artifact_path must be absolute or project relative")
#         return p

#     def model_dump(self, **kwargs) -> dict:
#         return super().model_dump(**kwargs)
