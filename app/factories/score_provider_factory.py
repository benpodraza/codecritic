from app.factories.base_provider_factory import BaseProviderFactory
from app.db.models import ScoreProviderConfig
from app.providers.score_provider_base import ScoreProviderBase

class ScoreProviderFactory(BaseProviderFactory):
    config_model = ScoreProviderConfig
    base_class = ScoreProviderBase

    @classmethod
    def create(cls, id: int, **kwargs) -> ScoreProviderBase:
        instance = super().create(id, **kwargs)
        config = instance.config.config or {}

        # ⏱️ Delayed imports to prevent circular references
        if "tool_provider_ids" in config or "context_provider_id" in config:
            from app.factories.tool_provider_factory import ToolProviderFactory
            from app.factories.context_provider_factory import ContextProviderFactory

            if (ctx_id := config.get("context_provider_id")):
                context = ContextProviderFactory.create(ctx_id)
                instance.set_context_provider(context)
                if hasattr(context, "set_score_provider"):
                    context.set_score_provider(instance)

            for _, tool_id in (config.get("tool_provider_ids") or {}).items():
                tool = ToolProviderFactory.create(tool_id)
                instance.set_tool_provider(tool)

        return instance
