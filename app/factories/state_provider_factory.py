from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import StateProviderConfig
from app.providers.state_provider_base import StateProviderBase

class StateProviderFactory(BaseProviderFactory):
    config_model = StateProviderConfig
    base_class = StateProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> StateProviderBase:
        # Delayed imports to avoid circular dependencies
        from app.factories.agent_provider_factory import AgentProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        engine = kwargs.get("engine")
        preload_instance = super().create(id, engine=engine)
        config = preload_instance.config.config or {}

        # Inject agents into a dict
        kwargs["agents"] = {
            name: AgentProviderFactory.create(agent_id)
            for name, agent_id in config.get("agents", {}).items()
        }

        # Inject optional context/score/tools
        if "context_provider_id" in config:
            kwargs["context_provider"] = ContextProviderFactory.create(config["context_provider_id"])

        if "score_provider_id" in config:
            kwargs["score_provider"] = ScoreProviderFactory.create(config["score_provider_id"])

        kwargs["tool_providers"] = [
            ToolProviderFactory.create(tool_id)
            for _, tool_id in (config.get("tool_provider_ids") or {}).items()
        ]

        return super().create(id, **kwargs)
