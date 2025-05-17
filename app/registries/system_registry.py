from enum import Enum
from pydantic import BaseModel
from typing import List

class TransitionFunction(Enum):
    DEFAULT = "default"
    CUSTOM = "custom"

class SystemEntry(BaseModel):
    name: str
    agents: List[str]
    transition_function: TransitionFunction

SYSTEM_REGISTRY = {
    "refactoring": SystemEntry(
        name="Refactoring",
        agents=["generator", "discriminator", "mediator"],
        transition_function=TransitionFunction.DEFAULT,
    ),
    "linting": SystemEntry(
        name="Linting",
        agents=["generator", "discriminator"],
        transition_function=TransitionFunction.CUSTOM,
    ),
    "docstring": SystemEntry(
        name="Docstring",
        agents=["generator", "mediator"],
        transition_function=TransitionFunction.DEFAULT,
    ),
    "unit_testing": SystemEntry(
        name="UnitTesting",
        agents=["generator", "discriminator", "mediator", "patchor"],
        transition_function=TransitionFunction.DEFAULT,
    ),
}
