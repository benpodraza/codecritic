from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class Repo:
    name: str
    full_name: str
    private: bool
    default_branch: str
    owner: str


@dataclass
class TreeItem:
    path: str
    type: Literal["blob", "tree"]
    sha: str
    size: Optional[int] = None


@dataclass
class FileVersion:
    sha: str
    date: str
    author: str
    message: str
