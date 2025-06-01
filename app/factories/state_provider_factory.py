from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import StateProviderConfig
from app.providers.state_provider_base import StateProviderBase

class StateProviderFactory(BaseProviderFactory):
    config_model = StateProviderConfig
    base_class = StateProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> StateProviderBase:
        from app.factories.agent_provider_factory import AgentProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        preload_instance = super().create(id, **kwargs)
        config = preload_instance.config.config or {}
        agents = {
            name: AgentProviderFactory.create(agent_id)
            for name, agent_id in config.get("agents", {}).items()
        }

        context_provider = (
            ContextProviderFactory.create(config["context_provider_id"])
            if config.get("context_provider_id") else None
        )

        score_provider = (
            ScoreProviderFactory.create(config["score_provider_id"])
            if config.get("score_provider_id") else None
        )

        tool_providers = [
            ToolProviderFactory.create(tool_id)
            for _, tool_id in (config.get("tool_provider_ids") or {}).items()
        ]

        cls_type = type(preload_instance)
        return cls_type(
            config=preload_instance.config,
            engine=preload_instance._engine,
            agents=agents,
            context_provider=context_provider,
            score_provider=score_provider,
            tool_providers=tool_providers
        )
