from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import AgentProviderConfig
from app.providers.agent_provider_base import AgentProviderBase
from app.enums.logging_enums import PROVIDER_TYPE


class AgentProviderFactory(BaseProviderFactory):
    config_model = AgentProviderConfig
    base_class   = AgentProviderBase

    @classmethod
    def create(
        cls,
        id: int,
        *,
        called_by_type: PROVIDER_TYPE | None = None,
        called_by_id: int | None = None,
        **kwargs
    ) -> AgentProviderBase:
        # delayed imports to avoid circular dependencies
        from app.factories.agent_engine_provider_factory import AgentEngineProviderFactory
        from app.factories.prompt_provider_factory      import PromptProviderFactory
        from app.factories.context_provider_factory     import ContextProviderFactory
        from app.factories.score_provider_factory       import ScoreProviderFactory
        from app.factories.tool_provider_factory        import ToolProviderFactory

        # 1) Preload base instance to get config/engine/type
        preload_instance = super().create(
            id,
            called_by_type=called_by_type,
            called_by_id=called_by_id,
        )

        config = preload_instance._config.config or {}
        provider_id = preload_instance._config.id
        provider_type = preload_instance._infer_provider_type()

        # 2) Construct dependencies, passing caller identity
        agent_engine = (
            AgentEngineProviderFactory.create(
                config["agent_engine_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id
            ) if config.get("agent_engine_provider_id") else None
        )

        prompt_provider = (
            PromptProviderFactory.create(
                config["prompt_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id
            ) if config.get("prompt_provider_id") else None
        )

        context_provider = (
            ContextProviderFactory.create(
                config["context_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id
            ) if config.get("context_provider_id") else None
        )

        score_provider = (
            ScoreProviderFactory.create(
                config["score_provider_id"],
                called_by_type=provider_type,
                called_by_id=provider_id
            ) if config.get("score_provider_id") else None
        )

        tool_providers = [
            ToolProviderFactory.create(
                tid,
                called_by_type=provider_type,
                called_by_id=provider_id
            )
            for tid in (config.get("tool_provider_ids") or {}).values()
        ]

        # 3) Build final typed instance with dependencies
        cls_type = type(preload_instance)
        return cls_type(
            config           = preload_instance._config,
            agent_engine     = agent_engine,
            prompt_provider  = prompt_provider,
            context_provider = context_provider,
            score_provider   = score_provider,
            tool_providers   = tool_providers,
            called_by_type   = called_by_type,
            called_by_id     = called_by_id,
        )
