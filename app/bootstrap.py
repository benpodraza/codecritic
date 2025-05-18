from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Type

from .factories.agent import AgentFactory
from .factories.prompt_manager import PromptGeneratorFactory
from .registries.context_providers import CONTEXT_PROVIDER_REGISTRY
from .factories.tool_provider import ToolProviderFactory
from .factories.scoring_provider import ScoringProviderFactory
from .factories.state_manager import StateManagerFactory
from .factories.experiment_config_provider import ExperimentConfigProvider
from .abstract_classes.agent_base import AgentBase
from .abstract_classes.prompt_generator_base import PromptGeneratorBase
from .abstract_classes.tool_provider_base import ToolProviderBase
from .abstract_classes.scoring_provider_base import ScoringProviderBase
from .abstract_classes.state_manager_base import StateManagerBase

from .utilities.schema import initialize_database


def _import_class(path: str | Path, base_cls: Type) -> Type:
    mod_path = str(path).replace("\\", "/")
    if mod_path.endswith(".py"):
        mod_path = mod_path[:-3]
    mod_path = mod_path.replace("/", ".")
    module = import_module(f"app.extensions.{mod_path}")
    for attr in module.__dict__.values():
        if (
            isinstance(attr, type)
            and issubclass(attr, base_cls)
            and attr is not base_cls
        ):
            return attr
    raise ImportError(f"No subclass of {base_cls.__name__} found in {module.__name__}")


def seed_registries(reset_db: bool = False) -> None:
    conn = initialize_database(reset=reset_db)
    cur = conn.cursor()

    # Tool providers
    for row in cur.execute("SELECT name, artifact_path FROM tooling_provider"):
        name, artifact = row
        path = Path(artifact)
        cls = _import_class(path.as_posix(), ToolProviderBase)
        try:
            ToolProviderFactory.register(name, cls)
        except KeyError:
            pass

    # Context providers
    for row in cur.execute("SELECT name FROM context_provider"):
        (name,) = row
        # Assume providers are already registered via extensions
        if CONTEXT_PROVIDER_REGISTRY.get(name) is not None:
            continue

    # Prompt generators
    for row in cur.execute("SELECT name, artifact_path FROM prompt_generator"):
        name, artifact = row
        path = Path(artifact)
        cls = _import_class(path.as_posix(), PromptGeneratorBase)
        try:
            PromptGeneratorFactory.register(name, cls)
        except KeyError:
            pass

    # Agents
    for row in cur.execute("SELECT name, artifact_path FROM agent_config"):
        name, artifact = row
        path = Path(artifact)
        cls = _import_class(path.as_posix(), AgentBase)
        try:
            AgentFactory.register(name, cls)
        except KeyError:
            pass

    # Scoring providers
    for row in cur.execute("SELECT name, artifact_path FROM scoring_provider"):
        name, artifact = row
        path = Path(artifact)
        cls = _import_class(path.as_posix(), ScoringProviderBase)
        try:
            ScoringProviderFactory.register(name, cls)
        except KeyError:
            pass

    # State managers
    for row in cur.execute("SELECT name, artifact_path FROM state_manager"):
        name, artifact = row
        path = Path(artifact)
        cls = _import_class(path.as_posix(), StateManagerBase)
        try:
            StateManagerFactory.register(name, cls)
        except KeyError:
            pass

    # System managers are loaded via extensions; only register configs
    for row in cur.execute(
        "SELECT id, system_manager_id, scoring_model_id FROM experiment_config"
    ):
        config_id, system_manager_id, scoring_model_id = row
        config = {
            "system_manager_id": system_manager_id,
            "scoring_model_id": scoring_model_id,
        }
        ExperimentConfigProvider.register(config_id, config)

    conn.close()


if __name__ == "__main__":
    seed_registries(reset_db=True)
