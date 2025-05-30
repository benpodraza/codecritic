from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import AgentProviderConfig
from app.providers.agent_provider_base import AgentProviderBase

class AgentProviderFactory(BaseProviderFactory):
    config_model = AgentProviderConfig
    base_class   = AgentProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> AgentProviderBase:
        # delayed imports to avoid circular dependencies
        from app.factories.agent_engine_provider_factory import AgentEngineProviderFactory
        from app.factories.prompt_provider_factory      import PromptProviderFactory
        from app.factories.context_provider_factory     import ContextProviderFactory
        from app.factories.score_provider_factory       import ScoreProviderFactory
        from app.factories.tool_provider_factory        import ToolProviderFactory

        # 1) Preload via BaseProviderFactory (it will inject the DB engine for you)
        preload_instance = super().create(id)
        config           = preload_instance.config.config or {}

        # 2) Build each dependency exactly once
        agent_engine    = (
            AgentEngineProviderFactory.create(config["agent_engine_provider_id"])
            if config.get("agent_engine_provider_id") else None
        )
        prompt_provider = (
            PromptProviderFactory.create(config["prompt_provider_id"])
            if config.get("prompt_provider_id") else None
        )
        context_provider = (
            ContextProviderFactory.create(config["context_provider_id"])
            if config.get("context_provider_id") else None
        )
        score_provider  = (
            ScoreProviderFactory.create(config["score_provider_id"])
            if config.get("score_provider_id") else None
        )
        tool_providers  = [
            ToolProviderFactory.create(tid)
            for tid in (config.get("tool_provider_ids") or {}).values()
        ]

        # 3) Re-instantiate the actual subclass with all dependencies and the injected engine
        cls_type = type(preload_instance)
        return cls_type(
            config          = preload_instance.config,
            engine          = preload_instance._engine,
            agent_engine    = agent_engine,
            prompt_provider = prompt_provider,
            context_provider= context_provider,
            score_provider  = score_provider,
            tool_providers  = tool_providers,
        )
