from __future__ import annotations

from enum import Enum


class AgentRole(Enum):
    CRITIC = "critic"
    TESTER = "tester"
    FIXER = "fixer"
