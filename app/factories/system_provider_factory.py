from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import SystemProviderConfig
from app.providers.system_provider_base import SystemProviderBase

class SystemProviderFactory(BaseProviderFactory):
    config_model = SystemProviderConfig
    base_class = SystemProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> SystemProviderBase:
        # ⏱️ Delayed imports to avoid circular dependencies
        from app.factories.state_provider_factory import StateProviderFactory
        from app.factories.context_provider_factory import ContextProviderFactory
        from app.factories.score_provider_factory import ScoreProviderFactory
        from app.factories.tool_provider_factory import ToolProviderFactory

        engine = kwargs.get("engine")
        preload_instance = super().create(id, engine=engine)
        config = preload_instance.config.config or {}

        # Inject optional providers
        if "context_provider_id" in config:
            kwargs["context_provider"] = ContextProviderFactory.create(config["context_provider_id"])

        if "score_provider_id" in config:
            kwargs["score_provider"] = ScoreProviderFactory.create(config["score_provider_id"])

        kwargs["tool_providers"] = [
            ToolProviderFactory.create(tool_id)
            for _, tool_id in (config.get("tool_provider_ids") or {}).items()
        ]

        return super().create(id, **kwargs)
